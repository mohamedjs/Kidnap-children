<?php

namespace App\Http\Controllers\Frontend;

use App\Http\Repository\PostRepository;
use App\Http\Requests\Frontend\PostRequest;
use App\Http\Services\PostServices;
use App\Models\Post;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Events\PostEvent;
use App\Events\Notification;

class PostController extends Controller
{
    /**
     * @var PostServices
     */
    private $postServices;
    /**
     * @var PostRepository
     */
    private $postRepository;


    /**
     * PostController constructor.
     * @param PostServices $postServices
     */
    public function __construct(PostServices $postServices, PostRepository $postRepository)
    {
        $this->postServices = $postServices;
        $this->postRepository = $postRepository;
    }

    public function index(Request $request)
    {
        $posts = $this->postRepository->PostsWithFiltration(request())->simplePaginate(2);
        $posts->appends($request->all());
        return response()->json(["message" => "All Posts with pagination", "status" => true, "posts" => $posts]);
    }

    public function store(PostRequest $request)
    {
        $post = $this->postServices->fillPostFromRequest($request);
        $users = [];
        broadcast(new PostEvent($post))->toOthers();
        broadcast(new Notification(' add new post'))->toOthers();
        $results = $this->check_image($request,$post->id);
        foreach ($results as $key => $value) {
          array_push($users,$value->user_id);
        }
        $this->add_notify(Null,' add new post',$post->id);
        $this->add_notify($users,' upload post may be help you in info you need',$post->id);
        broadcast(new Notification(' upload post may be help you in info you need' , $users))->toOthers();
        return response()->json(["message" => "post is stored", "status" => true, 'post'=> $post , 'results' => $results]);
    }

    public function update(PostRequest $request, Post $post)
    {
        $post = $this->postServices->fillPostFromRequest($request, $post);
        return response()->json(["message" => "post is stored", "status" => true, compact('post')]);
    }

    public function destroy(Post $post)
    {
        $post->delete();
        return response()->json(["message" => "post is deleted", "status" => true]);
    }
}
