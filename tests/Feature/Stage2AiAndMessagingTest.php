<?php

namespace Tests\Feature;

use App\Events\AiMatchFound;
use App\Events\ChatMessageSent;
use App\Jobs\ProcessImageWithAIService;
use App\Models\AiMatch;
use App\Models\Chat;
use App\Models\Notification;
use App\Models\Post;
use App\Models\PostImage;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Event;
use Illuminate\Support\Facades\Queue;
use Laravel\Passport\Passport;
use Tests\TestCase;

class Stage2AiAndMessagingTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->artisan('passport:install');
    }

    public function test_can_send_private_message_and_broadcast_event()
    {
        Event::fake([ChatMessageSent::class]);

        $sender = factory(User::class)->create();
        $recipient = factory(User::class)->create();

        Passport::actingAs($sender);

        $response = $this->postJson('/api/messages', [
            'reciever_id' => $recipient->id,
            'message'     => 'Hello! Have you seen this child?',
        ]);

        $response->assertStatus(201)
                 ->assertJsonStructure(['message', 'chat' => ['id', 'sender_id', 'reciever_id', 'message']]);

        $this->assertDatabaseHas('chats', [
            'sender_id'   => $sender->id,
            'reciever_id' => $recipient->id,
            'message'     => 'Hello! Have you seen this child?',
        ]);

        $this->assertDatabaseHas('notifications', [
            'send_id'    => $sender->id,
            'receive_id' => $recipient->id,
            'type'       => 'chat',
        ]);

        Event::assertDispatched(ChatMessageSent::class, function ($event) use ($sender, $recipient) {
            return $event->chat->sender_id === $sender->id &&
                   $event->chat->reciever_id === $recipient->id;
        });
    }

    public function test_cannot_send_message_to_self()
    {
        $user = factory(User::class)->create();
        Passport::actingAs($user);

        $response = $this->postJson('/api/messages', [
            'reciever_id' => $user->id,
            'message'     => 'Self message',
        ]);

        $response->assertStatus(422);
    }

    public function test_can_get_conversations_and_messages()
    {
        $user1 = factory(User::class)->create();
        $user2 = factory(User::class)->create();

        Chat::create([
            'sender_id'   => $user1->id,
            'reciever_id' => $user2->id,
            'message'     => 'Message from user 1',
            'seen'        => 0,
        ]);

        Chat::create([
            'sender_id'   => $user2->id,
            'reciever_id' => $user1->id,
            'message'     => 'Response from user 2',
            'seen'        => 0,
        ]);

        Passport::actingAs($user1);

        $convResponse = $this->getJson('/api/messages/conversations');
        $convResponse->assertStatus(200)
                     ->assertJsonStructure(['conversations' => [['user', 'last_message', 'unread_count']]]);

        $msgResponse = $this->getJson("/api/messages/{$user2->id}");
        $msgResponse->assertStatus(200)
                    ->assertJsonStructure(['recipient_id', 'messages']);

        $this->assertEquals(2, count($msgResponse->json('messages')));

        // Verify incoming message was marked as read
        $this->assertDatabaseHas('chats', [
            'sender_id'   => $user2->id,
            'reciever_id' => $user1->id,
            'seen'        => 1,
        ]);
    }

    public function test_can_get_notifications_and_mark_as_read()
    {
        $sender = factory(User::class)->create();
        $receiver = factory(User::class)->create();

        $notification1 = Notification::create([
            'send_id'          => $sender->id,
            'receive_id'       => $receiver->id,
            'title'            => 'Alert 1',
            'content'          => 'Test notification 1',
            'notification_url' => '/api/posts/1',
            'type'             => 'ai_match',
            'seen'             => 0,
        ]);

        $notification2 = Notification::create([
            'send_id'          => $sender->id,
            'receive_id'       => $receiver->id,
            'title'            => 'Alert 2',
            'content'          => 'Test notification 2',
            'notification_url' => '/api/posts/2',
            'type'             => 'chat',
            'seen'             => 0,
        ]);

        Passport::actingAs($receiver);

        $response = $this->getJson('/api/notifications');
        $response->assertStatus(200);
        $this->assertEquals(2, $response->json('unread_count'));

        $readOne = $this->postJson("/api/notifications/{$notification1->id}/read");
        $readOne->assertStatus(200);
        $this->assertDatabaseHas('notifications', ['id' => $notification1->id, 'seen' => 1]);

        $readAll = $this->postJson('/api/notifications/read-all');
        $readAll->assertStatus(200);
        $this->assertDatabaseHas('notifications', ['id' => $notification2->id, 'seen' => 1]);
    }

    public function test_post_creation_dispatches_ai_job()
    {
        Queue::fake();

        $user = factory(User::class)->create();
        Passport::actingAs($user);

        $response = $this->postJson('/api/posts', [
            'name'        => 'Child With Image',
            'type'        => 'missed',
            'gender'      => 'male',
            'age'         => 6,
            'description' => 'Dispatched AI job test',
        ]);

        $response->assertStatus(201);
        $postId = $response->json('post.id');

        // Manually trigger process endpoint to verify queue dispatch
        $processResponse = $this->postJson("/api/posts/{$postId}/process-ai");
        $processResponse->assertStatus(200);

        Queue::assertPushed(ProcessImageWithAIService::class);
    }

    public function test_ai_matches_persistence_and_retrieval()
    {
        Event::fake([AiMatchFound::class]);

        $user1 = factory(User::class)->create();
        $user2 = factory(User::class)->create();

        $post1 = factory(Post::class)->create(['user_id' => $user1->id, 'name' => 'Child 1']);
        $post2 = factory(Post::class)->create(['user_id' => $user2->id, 'name' => 'Child 2']);

        $aiMatch = AiMatch::create([
            'source_post_id'  => $post1->id,
            'matched_post_id' => $post2->id,
            'confidence'      => 87.5,
            'face_detected'   => true,
            'status'          => 'matched',
            'raw_response'    => json_encode(['matches' => [['post_id' => $post2->id, 'confidence' => 87.5]]]),
        ]);

        Passport::actingAs($user1);

        $userMatches = $this->getJson('/api/matches');
        $userMatches->assertStatus(200)
                    ->assertJsonStructure(['matches' => ['data']]);

        $this->assertEquals(1, count($userMatches->json('matches.data')));

        $postMatches = $this->getJson("/api/posts/{$post1->id}/matches");
        $postMatches->assertStatus(200)
                   ->assertJsonStructure(['post', 'matches']);

        $this->assertEquals(87.5, $postMatches->json('matches.0.confidence'));
    }

    public function test_ai_job_fallback_when_service_unavailable()
    {
        $user = factory(User::class)->create();
        $post = factory(Post::class)->create(['user_id' => $user->id]);
        
        // Attach image path
        PostImage::create([
            'post_id' => $post->id,
            'image'   => 'uploads/posts/test_dummy.jpg'
        ]);

        // Create dummy file for job execution
        $dummyPath = public_path('uploads/posts/test_dummy.jpg');
        if (!file_exists(dirname($dummyPath))) {
            mkdir(dirname($dummyPath), 0777, true);
        }
        file_put_contents($dummyPath, 'dummy image content');

        $job = new ProcessImageWithAIService($post);

        // Simulate failed exception handler
        $exception = new \Exception("AI Microservice Connection Refused");
        $job->failed($exception);

        $this->assertDatabaseHas('ai_matches', [
            'source_post_id' => $post->id,
            'status'         => 'failed',
            'face_detected'  => 0,
        ]);

        if (file_exists($dummyPath)) {
            unlink($dummyPath);
        }
    }
}
