<?php

namespace App\Jobs;

use App\Events\AiMatchFound;
use App\Models\AiMatch;
use App\Models\Notification;
use App\Models\Post;
use GuzzleHttp\Client;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Log;

class ProcessImageWithAIService implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public $post;
    public $tries = 3;
    public $backoff = [5, 15, 30];

    /**
     * Create a new job instance.
     *
     * @param Post $post
     */
    public function __construct(Post $post)
    {
        $this->post = $post;
    }

    /**
     * Execute the job.
     *
     * @return void
     */
    public function handle()
    {
        $this->post->loadMissing('images');

        if ($this->post->images->isEmpty()) {
            Log::warning("ProcessImageWithAIService: Post #{$this->post->id} has no attached images.");
            return;
        }

        $baseUrl = rtrim(env('AI_SERVICE_URL', 'http://127.0.0.1:8000'), '/');
        $client = new Client([
            'base_uri' => $baseUrl,
            'timeout'  => 15.0,
        ]);

        foreach ($this->post->images as $postImage) {
            $relativePath = ltrim($postImage->image, '/');
            $fullPath = public_path($relativePath);

            if (!file_exists($fullPath)) {
                $fullPath = base_path($relativePath);
            }

            if (!file_exists($fullPath)) {
                Log::error("ProcessImageWithAIService: Image file not found at {$fullPath} for Post #{$this->post->id}.");
                continue;
            }

            try {
                // 1. Index post image in AI microservice
                $indexResponse = $client->post('/api/v1/index', [
                    'multipart' => [
                        [
                            'name'     => 'post_id',
                            'contents' => (string) $this->post->id,
                        ],
                        [
                            'name'     => 'file',
                            'contents' => fopen($fullPath, 'r'),
                            'filename' => basename($fullPath),
                        ],
                    ],
                ]);

                Log::info("AI Index response for Post #{$this->post->id}: " . $indexResponse->getBody()->getContents());

                // 2. Compare post image against indexed database
                $compareResponse = $client->post('/api/v1/compare', [
                    'query' => [
                        'top_k'          => 10,
                        'min_confidence' => 0.0,
                    ],
                    'multipart' => [
                        [
                            'name'     => 'file',
                            'contents' => fopen($fullPath, 'r'),
                            'filename' => basename($fullPath),
                        ],
                    ],
                ]);

                $responseData = json_decode($compareResponse->getBody()->getContents(), true);

                if (empty($responseData) || !isset($responseData['matches'])) {
                    Log::warning("AI Compare response invalid or empty for Post #{$this->post->id}.");
                    continue;
                }

                $faceDetected = $responseData['face_detected'] ?? true;
                $matches = $responseData['matches'] ?? [];

                if (!$faceDetected) {
                    Log::info("ProcessImageWithAIService: No face detected in Post #{$this->post->id} image.");
                    AiMatch::updateOrCreate(
                        [
                            'source_post_id' => $this->post->id,
                            'matched_post_id' => $this->post->id,
                        ],
                        [
                            'confidence'    => 0.0,
                            'face_detected' => false,
                            'status'        => 'no_face',
                            'raw_response'  => json_encode($responseData),
                        ]
                    );
                    continue;
                }

                foreach ($matches as $match) {
                    $matchedPostId = (int) ($match['post_id'] ?? 0);
                    $confidence = (float) ($match['confidence'] ?? 0.0);

                    if (!$matchedPostId || $matchedPostId === (int) $this->post->id) {
                        continue;
                    }

                    $matchedPost = Post::find($matchedPostId);
                    if (!$matchedPost) {
                        continue;
                    }

                    $aiMatch = AiMatch::updateOrCreate(
                        [
                            'source_post_id'  => $this->post->id,
                            'matched_post_id' => $matchedPostId,
                        ],
                        [
                            'confidence'    => $confidence,
                            'face_detected' => true,
                            'status'        => 'matched',
                            'raw_response'  => json_encode($responseData),
                        ]
                    );

                    // Sync legacy post_results table
                    $this->post->results()->syncWithoutDetaching([$matchedPostId]);

                    // Generate notification for matched post owner
                    $msg = "AI Match Found: Post #{$this->post->id} matches Post #{$matchedPostId} with {$confidence}% confidence.";
                    
                    if ($matchedPost->user_id) {
                        Notification::create([
                            'send_id'          => $this->post->user_id ?? $matchedPost->user_id,
                            'receive_id'       => $matchedPost->user_id,
                            'title'            => 'AI Child Match Found',
                            'content'          => $msg,
                            'notification_url' => "/api/posts/{$this->post->id}",
                            'type'             => 'ai_match',
                            'seen'             => 0,
                        ]);
                        event(new AiMatchFound($aiMatch, $matchedPost->user_id, $msg));
                    }

                    // Generate notification for source post owner if different
                    if ($this->post->user_id && $this->post->user_id !== $matchedPost->user_id) {
                        Notification::create([
                            'send_id'          => $matchedPost->user_id ?? $this->post->user_id,
                            'receive_id'       => $this->post->user_id,
                            'title'            => 'AI Child Match Found',
                            'content'          => $msg,
                            'notification_url' => "/api/posts/{$matchedPostId}",
                            'type'             => 'ai_match',
                            'seen'             => 0,
                        ]);
                        event(new AiMatchFound($aiMatch, $this->post->user_id, $msg));
                    }
                }
            } catch (\Throwable $e) {
                Log::error("ProcessImageWithAIService error for Post #{$this->post->id}: " . $e->getMessage());
                throw $e;
            }
        }
    }

    /**
     * Handle job failure.
     *
     * @param \Throwable $exception
     * @return void
     */
    public function failed(\Throwable $exception)
    {
        Log::error("ProcessImageWithAIService permanently failed for Post #{$this->post->id}: " . $exception->getMessage());

        try {
            AiMatch::updateOrCreate(
                [
                    'source_post_id'  => $this->post->id,
                    'matched_post_id' => $this->post->id,
                ],
                [
                    'confidence'    => 0.0,
                    'face_detected' => false,
                    'status'        => 'failed',
                    'raw_response'  => json_encode(['error' => $exception->getMessage()]),
                ]
            );
        } catch (\Throwable $ex) {
            Log::error("Failed to store AI match failure record: " . $ex->getMessage());
        }
    }
}
