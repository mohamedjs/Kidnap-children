<?php

namespace App\Http\Controllers;

use Illuminate\Foundation\Bus\DispatchesJobs;
use Illuminate\Routing\Controller as BaseController;
use Illuminate\Foundation\Validation\ValidatesRequests;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;
use App\Models\Notification;
use App\Models\Post;
use App\Models\PostImage;
use GuzzleHttp\Client;
use GuzzleHttp\HandlerStack;
use GuzzleHttp\Middleware;
use Psr\Http\Message\RequestInterface;
use Illuminate\Http\Request;
class Controller extends BaseController
{
    use AuthorizesRequests, DispatchesJobs, ValidatesRequests;

    public function add_notify($users = Null,$message,$post_id)
    {
      if($users)
      {
        if(is_array($users))
        {
          foreach ($users as $current_user) {
              Notification::create([
                'send_id' => \Auth::id(),
                'receive_id' => $current_user,
                'title' => \Auth::user()->name.$message,
                'content' => \Auth::user()->name.$message,
                'notification_url' => url('get_post/'.$post_id)
              ]);
          }
        }
        else
        {
          Notification::create([
            'send_id' => \Auth::id(),
            'receive_id' => $users->id,
            'title' => \Auth::user()->name.$message,
            'content' => \Auth::user()->name.$message,
            'notification_url' => url('get_post/'.$post_id)
          ]);
        }
      }
      else
      {
        $all_user = \App\Models\User::whereNotIn('id',[\Auth::id()])->get();
        foreach ($all_user as $current_user) {
          Notification::create([
            'send_id' => \Auth::id(),
            'receive_id' => $current_user->id,
            'title' => \Auth::user()->name.$message,
            'content' => \Auth::user()->name.$message,
            'notification_url' => url('get_post/'.$post_id)
          ]);
        }
      }
    }

    public function check_image(Request $request , $po_id)
    {
      $arr = [];
      $output = [];
      $post_id = [];
      $posts = [];
      $post = Post::find($po_id);
      $post_images = $post->images;
      $images = $request->images;
      foreach ($images as $key=> $image) {
        $value['image'] = $image;
        array_push($arr,$value);
        if ( ! is_array( $image ) ) {
           $output[] = [
              'name'     => 'file[]',
              'contents' => fopen( $_SERVER['DOCUMENT_ROOT'].parse_url($post_images[$key]->image)['path'], 'r' ),
              'filename' => $image->getClientOriginalName()
           ];
           continue;
        }
      }
        $client = new Client(['base_uri' => 'https://api-missed-gb.herokuapp.com/']);
        $response = $client->request('POST', '/api/detect_image',[
        'multipart' => $output]);
        //return json_decode($response);
        $id = json_decode($response->getBody()) ;
        if(is_array($id) && count($id) > 0 )
        {
          $post_id = PostImage::whereIn('id',$id)->groupBy('post_id')->pluck('post_id')->toArray();
          $post->results()->attach($post_id);
          $posts = Post::with(["images", "user", "comments" => function ($query) {
              $query->with("user");
              $query->take(0);
          }])->withCount('comments as count_comment')->whereIn('id',$post_id)->whereNotIn('id',[$po_id])->get();
        }
        return $posts;
    }
}
