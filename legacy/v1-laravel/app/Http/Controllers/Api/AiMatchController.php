<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Jobs\ProcessImageWithAIService;
use App\Models\AiMatch;
use App\Models\Post;
use Illuminate\Http\Request;

class AiMatchController extends Controller
{
    /**
     * Get all AI matches relevant to authenticated user's posts.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function index(Request $request)
    {
        $userId = $request->user()->id;

        $userPostIds = Post::where('user_id', $userId)->pluck('id');

        $matches = AiMatch::with(['sourcePost.images', 'sourcePost.user', 'matchedPost.images', 'matchedPost.user'])
            ->whereIn('source_post_id', $userPostIds)
            ->orWhereIn('matched_post_id', $userPostIds)
            ->orderBy('confidence', 'desc')
            ->paginate(15);

        return response()->json([
            'matches' => $matches
        ]);
    }

    /**
     * Get AI matches for a specific post.
     *
     * @param Request $request
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function showForPost(Request $request, $id)
    {
        $post = Post::findOrFail($id);

        $matches = AiMatch::with(['sourcePost.images', 'sourcePost.user', 'matchedPost.images', 'matchedPost.user'])
            ->where('source_post_id', $post->id)
            ->orWhere('matched_post_id', $post->id)
            ->orderBy('confidence', 'desc')
            ->get();

        return response()->json([
            'post'    => $post->load(['images', 'user']),
            'matches' => $matches
        ]);
    }

    /**
     * Trigger manual AI image recognition process for a post.
     *
     * @param Request $request
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function processPost(Request $request, $id)
    {
        $post = Post::findOrFail($id);

        ProcessImageWithAIService::dispatch($post);

        return response()->json([
            'message' => "AI image processing job dispatched for Post #{$post->id}.",
            'post'    => $post
        ]);
    }
}
