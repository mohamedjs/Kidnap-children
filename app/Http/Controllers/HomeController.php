<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\User;
use Auth;
use App\Post;
class HomeController extends Controller
{
//    /**
//     * Show the application dashboard.
//     *
//     * @return \Illuminate\Contracts\Support\Renderable
//     */
   public function index()
   {
       return view('front.home');
   }
//
//    public function get_posts()
//    {
//      $posts = Post::with(['user','images','region'])->with(['comments'=>function($q){
//        $q->with('user')
//        ->paginate(2);
//      }])->orderBy('created_at','asc')->simplePaginate(2);
//      return $posts;
//    }
//    public function profile()
//    {
//      $user = Auth::user();
//      return view('front.profile',compact('user'));
//    }
}
