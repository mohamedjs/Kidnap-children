<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Like;
use App\Events\LikePost;
use App\Events\UnlikePost;
use Auth;
class LikeController extends Controller
{
    public function store(Request $request)
    {
      $id = $request->id;
      $like = Like::create([
        'user_id' => Auth::id(),
        'post_id' => $id
      ]);
      \Event::fire(new LikePost($like));
      return response()->json(['ok']);
    }

    public function destroy($id)
    {
      Like::where('user_id',Auth::id())->where('post_id',$id)->delete();
      \Event::fire(new UnlikePost(Auth::user()->name,$id));
      return response()->json(['ok']);
    }
}
