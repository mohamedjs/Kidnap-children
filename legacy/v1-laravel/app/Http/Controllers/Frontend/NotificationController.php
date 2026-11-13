<?php

namespace App\Http\Controllers\Frontend;

use App\Http\Controllers\Controller;
use App\Models\Notification;
use App\Models\Post;
use Illuminate\Http\Request;

class NotificationController extends Controller
{

    public function all_notification()
    {
      $notifications  = Notification::where('receive_id',\Auth::id())->get();
      return view('front.notification',compact('notifications'));
    }

    public function get_notification()
    {
      $notification  = Notification::where('receive_id',\Auth::id())->with('sender')->take(10)->orderBy('created_at','desc')->get();
      $unread_notify = Notification::where('receive_id',\Auth::id())->where('seen',0)->count();

      return response()->json([
        'status' => 'success' , 'message' => "get notification data" ,
         'notifications' => $notification , 'unread_notify' => $unread_notify
       ]);
    }

    public function inner_post($id)
    {
      $result_id = [];
      $post = Post ::with(["images", "user", "comments" => function ($query) {
          $query->with("user");
          $query->take(0);
      }])->withCount('comments as count_comment')->where('posts.id',$id)->first();
      $post_results = $post->results;
      foreach ($post_results as $result) {
        array_push($result_id,$result->id);
      }
      $results = Post ::with(["images", "user", "comments" => function ($query) {
          $query->with("user");
          $query->take(0);
      }])->withCount('comments as count_comment')->whereIn('posts.id',$result_id)->get();

      return view('front.inner_post',compact('post','results'));
    }
}
