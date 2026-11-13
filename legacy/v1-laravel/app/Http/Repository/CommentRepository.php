<?php
/**
 * Created by PhpStorm.
 * User: ghost
 * Date: 6/8/19
<<<<<<< HEAD
 * Time: 9:58 AM
=======
 * Time: 2:41 PM
>>>>>>> 3c5636b0f6f12e77909de0649b87ad24a8da0ff8
 */

namespace App\Http\Repository;

use App\Models\Comment;
use Illuminate\Database\Schema\Builder;
use Illuminate\Http\Request;

class CommentRepository
{
    /**
     * @param Request $request
     * @return Builder
     */
    public function getPostComment(Request $request)
    {
        $comment = Comment::query()->with("user")->where("post_id" , "=", $request->input("post_id"));
        return $comment;
    }
}
