<?php
/**
 * Created by PhpStorm.
 * User: ghost
 * Date: 6/8/19
 * Time: 10:17 AM
 */

namespace App\Http\Services;


use App\Models\Comment;
use Illuminate\Http\Request;

class CommentService
{
    public function fillCommentFromRequest(Request $request, Comment $comment = null)
    {
        if (!$comment) {
            $comment = new Comment();
        }

        $comment->fill($request->all());
        $comment->save() ;

        return $comment;
    }
}
