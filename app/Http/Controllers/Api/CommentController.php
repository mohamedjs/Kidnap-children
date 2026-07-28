<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\CommentStoreRequest;
use App\Models\Comment;
use App\Models\Post;
use Illuminate\Http\Request;

class CommentController extends Controller
{
    public function index($postId)
    {
        $post = Post::findOrFail($postId);
        $comments = $post->comments()->with('user')->orderBy('created_at', 'desc')->paginate(20);

        return response()->json($comments);
    }

    public function store(CommentStoreRequest $request, $postId)
    {
        $post = Post::findOrFail($postId);
        $user = $request->user();

        $comment = Comment::create([
            'user_id' => $user->id,
            'post_id' => $post->id,
            'comment' => $request->comment,
        ]);

        $comment->load('user');

        return response()->json([
            'message' => 'Comment added successfully',
            'comment' => $comment
        ], 201);
    }

    public function destroy(Request $request, $id)
    {
        $comment = Comment::findOrFail($id);
        $this->authorize('delete', $comment);

        $comment->delete();

        return response()->json([
            'message' => 'Comment deleted successfully'
        ]);
    }
}
