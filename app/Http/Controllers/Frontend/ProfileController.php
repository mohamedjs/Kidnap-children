<?php

namespace App\Http\Controllers\Frontend;

use App\Http\Controllers\Controller;
use App\Models\Notification;
use App\Models\Post;
use App\Models\User;
use Illuminate\Http\Request;
 use File;
class ProfileController extends Controller
{
    /**
     * Display a listing of the resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
        return view('front.profile');
    }

    public function foundperson()
    {
      return view('front.found_person');
    }
    public function missedperson()
    {
      return view('front.missed_person');
    }
    public function user_info()
    {
      return view('front.user');
    }
    public function update_user(Request $request)
    {
      $date_path = date("Y") . '/' . date("m") . '/' . date("d") . '/';
      $path = public_path() . '/front/uploads/users/' . $date_path;
      if (!File::exists($path)) {
          File::makeDirectory($path, 0777, true);
      }
      $file_name = date('YmdHis') . mt_rand() . '_'.'users'.'.' . $request->user_image->getClientOriginalExtension();
      $request->user_image->move($path, $file_name);
      $user_img = url('front/uploads/users/' . $date_path . $file_name);

      $request->request->add(['image' => $user_img]);
      //background iimage
      $date_path = date("Y") . '/' . date("m") . '/' . date("d") . '/';
      $path = public_path() . '/front/uploads/background/' . $date_path;
      if (!File::exists($path)) {
          File::makeDirectory($path, 0777, true);
      }
      $file_name = date('YmdHis') . mt_rand() . '_'.'background'.'.' . $request->user_background_image->getClientOriginalExtension();
      $request->user_background_image->move($path, $file_name);
      $background_img = url('front/uploads/background/' . $date_path . $file_name);

      $request->request->add(['background_image' => $background_img]);
      $user = User::find(\Auth::id())->update($request->all());
      return back();
    }
}
