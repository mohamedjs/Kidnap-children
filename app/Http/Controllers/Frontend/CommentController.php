<?php

namespace App\Http\Controllers\Frontend;

use App\Http\Repository\CommentRepository;
use App\Http\Requests\Frontend\CommentRequest;
use App\Http\Services\CommentServices;
use App\Models\Comment;
use App\Models\Post;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Events\CommentPost;
use App\Events\Notification;

class CommentController extends Controller
{
    /**
     * @var CommentRepository
     */
    private $commentRepository;
    /**
     * @var CommentServices
     */
    private $commentServices;

    /**
     * CommentController constructor.
     * @param CommentRepository $commentRepository
     * @param CommentServices $commentServices
     */
    public function __construct(CommentRepository $commentRepository, CommentServices $commentServices)
    {
        $this->commentRepository = $commentRepository;
        $this->commentServices = $commentServices;
    }

    public function index()
    {
        $comments = $this->commentRepository->getPostComment(\request())->simplePaginate(2);
        $comments->appends(request()->all());

        return response()->json([
            "message" => "post comments",
            "status" => true,
            "comments" => $comments
        ]);
    }

    public function store(CommentRequest $request)
    {
        $comment = $this->commentServices->fillCommentFromRequest($request);

        $comment = Comment::query()->with("user")->where("id", "=", $comment->id)->first();

        $post = Post::find($request->post_id);
        broadcast(new CommentPost($comment,$request->key))->toOthers();
        broadcast(new Notification(' comment in your post',$post->user))->toOthers();
        $this->add_notify($post->user,' comment in your post',$post->id);
        return response()->json([
            "message" => "post comments",
            "status" => true,
            "comment" => $comment
        ]);
    }

    public function update(CommentRequest $request, Comment $comment)
    {
        $comment = $this->commentServices->fillCommentFromRequest($request, $comment);

        $comment = Comment::query()->with("user")->where("id", "=", $comment->id)->first();

        return response()->json([
            "message" => "comment updated",
            "status" => true,
            "comment" => $comment
        ]);
    }

    public function destroy(Comment $comment)
    {
        $comment->delete();

        return response()->json([
            "message" => "delete comment",
            "status" => true,
            "comment" => []
        ]);
    }


}
