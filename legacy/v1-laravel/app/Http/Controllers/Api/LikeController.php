<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Like;
use App\Models\Post;
use Illuminate\Http\Request;

class LikeController extends Controller
{
    public function toggle(Request $request, $postId)
    {
        $post = Post::findOrFail($postId);
        $user = $request->user();

        $like = Like::where('user_id', $user->id)->where('post_id', $post->id)->first();

        if ($like) {
            $like->delete();
            $liked = false;
            $message = 'Post unliked successfully';
        } else {
            Like::create([
                'user_id' => $user->id,
                'post_id' => $post->id,
            ]);
            $liked = true;
            $message = 'Post liked successfully';
        }

        $likesCount = $post->likes()->count();

        return response()->json([
            'message' => $message,
            'liked' => $liked,
            'likes_count' => $likesCount
        ]);
    }

    public function index($postId)
    {
        $post = Post::findOrFail($postId);
        $likes = $post->likes()->with('user')->paginate(20);

        return response()->json($likes);
    }
}
