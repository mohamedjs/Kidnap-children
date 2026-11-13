<?php

namespace Tests\Feature;

use Tests\TestCase;
use App\Models\User;
use App\Models\Post;
use App\Models\Comment;
use App\Models\Like;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Laravel\Passport\Passport;

class ApiTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->artisan('passport:install');
    }

    public function test_user_can_register()
    {
        $response = $this->postJson('/api/auth/register', [
            'name' => 'John Doe',
            'email' => 'john@example.com',
            'password' => 'secret123',
            'phone' => '123456789',
            'address' => '123 Main St',
            'gender' => 'male',
            'birth_date' => '1995-05-05',
        ]);

        $response->assertStatus(201)
                 ->assertJsonStructure(['message', 'user', 'access_token']);

        $this->assertDatabaseHas('users', ['email' => 'john@example.com']);
    }

    public function test_user_can_login()
    {
        $user = factory(User::class)->create([
            'email' => 'testuser@example.com',
            'password' => bcrypt('password123'),
        ]);

        $response = $this->postJson('/api/auth/login', [
            'email' => 'testuser@example.com',
            'password' => 'password123',
        ]);

        $response->assertStatus(200)
                 ->assertJsonStructure(['message', 'user', 'access_token']);
    }

    public function test_cannot_login_with_invalid_credentials()
    {
        $response = $this->postJson('/api/auth/login', [
            'email' => 'invalid@example.com',
            'password' => 'wrongpass',
        ]);

        $response->assertStatus(401);
    }

    public function test_authenticated_user_can_get_profile()
    {
        $user = factory(User::class)->create();
        Passport::actingAs($user);

        $response = $this->getJson('/api/auth/me');
        $response->assertStatus(200);
        $this->assertEquals($user->email, $response->json('user.email'));
    }

    public function test_can_list_and_filter_posts()
    {
        $user = factory(User::class)->create();
        factory(Post::class)->create([
            'user_id' => $user->id,
            'name' => 'Missing Child Alex',
            'type' => 'missed',
            'gender' => 'male',
            'age' => 8,
        ]);

        $response = $this->getJson('/api/posts?type=missed&query=Alex');
        $response->assertStatus(200);
        $this->assertEquals('Missing Child Alex', $response->json('data.0.name'));
    }

    public function test_authenticated_user_can_create_post()
    {
        $user = factory(User::class)->create();
        Passport::actingAs($user);

        $response = $this->postJson('/api/posts', [
            'name' => 'Found Child Sam',
            'type' => 'founded',
            'gender' => 'female',
            'age' => 5,
            'description' => 'Found near park',
        ]);

        $response->assertStatus(201);
        $this->assertEquals('Found Child Sam', $response->json('post.name'));
        $this->assertDatabaseHas('posts', ['name' => 'Found Child Sam']);
    }

    public function test_user_can_update_own_post()
    {
        $user = factory(User::class)->create();
        $post = factory(Post::class)->create(['user_id' => $user->id]);
        Passport::actingAs($user);

        $response = $this->putJson("/api/posts/{$post->id}", [
            'name' => 'Updated Child Name',
        ]);

        $response->assertStatus(200);
        $this->assertEquals('Updated Child Name', $response->json('post.name'));
    }

    public function test_user_cannot_update_others_post()
    {
        $owner = factory(User::class)->create();
        $otherUser = factory(User::class)->create();
        $post = factory(Post::class)->create(['user_id' => $owner->id]);
        Passport::actingAs($otherUser);

        $response = $this->putJson("/api/posts/{$post->id}", [
            'name' => 'Hacked Name',
        ]);

        $response->assertStatus(403);
    }

    public function test_user_can_comment_on_post()
    {
        $user = factory(User::class)->create();
        $post = factory(Post::class)->create();
        Passport::actingAs($user);

        $response = $this->postJson("/api/posts/{$post->id}/comments", [
            'comment' => 'I saw this child near the station!',
        ]);

        $response->assertStatus(201);
        $this->assertEquals('I saw this child near the station!', $response->json('comment.comment'));
        $this->assertDatabaseHas('comments', ['comment' => 'I saw this child near the station!']);
    }

    public function test_user_can_toggle_like_on_post()
    {
        $user = factory(User::class)->create();
        $post = factory(Post::class)->create();
        Passport::actingAs($user);

        $response = $this->postJson("/api/posts/{$post->id}/like");
        $response->assertStatus(200);
        $this->assertTrue($response->json('liked'));
        $this->assertEquals(1, $response->json('likes_count'));

        $response2 = $this->postJson("/api/posts/{$post->id}/like");
        $response2->assertStatus(200);
        $this->assertFalse($response2->json('liked'));
        $this->assertEquals(0, $response2->json('likes_count'));
    }

    public function test_search_endpoint()
    {
        $user = factory(User::class)->create();
        factory(Post::class)->create([
            'user_id' => $user->id,
            'name' => 'Unique Child Name',
            'type' => 'missed',
        ]);

        $response = $this->getJson('/api/search?query=Unique&type=missed');
        $response->assertStatus(200);
        $this->assertEquals('Unique Child Name', $response->json('data.0.name'));
    }
}
