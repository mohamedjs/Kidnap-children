<?php
/**
 * Created by PhpStorm.
 * User: ghost
 * Date: 6/8/19
 * Time: 8:54 AM
 */

namespace App\Http\Repository;


use App\Post;
use Illuminate\Http\Request;

class PostRepository
{
    public function PostsWithFiltration(Request $request)
    {
        $posts = Post::with(["images", "user", "comments" => function ($query) {
            $query->with("user");
            $query->take(0);
        }])->withCount('comments as count_comment');

        if ($request->has("user_id") && $request->input("user_id") != '') {
            $posts = $posts->where("user_id", '=', $request->input("user_id"));
        }

        if ($request->has("gender") && $request->input("gender") != '') {
            $posts = $posts->where("gender", '=', $request->input("gender"));
        }

        if ($request->has("type") && $request->input("type") != '') {
            $posts = $posts->where("type", '=', $request->input("type"));
        }

        if ($request->has("from") && $request->input("from") != '') {
            $posts = $posts->where("age", '>=', $request->input("from"));
        }

        if ($request->has("to") && $request->input("to") != '') {
            $posts = $posts->where("age", '<=', $request->input("to"));
        }

        $posts = $posts->orderBy('posts.created_at', 'desc');

        return $posts;
    }
}
