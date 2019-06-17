<?php

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/
//\Illuminate\Support\Facades\Auth::loginUsingId(1);
Route::get('/test', function () {
    return view('welcome');
});

Auth::routes();

Route::prefix('/')->attribute('namespace', 'Frontend')->middleware('auth')->group(function () {
    Route::resource("posts", "PostController");
    Route::resource("comments", "CommentController");
    Route::resource("profile", "ProfileController");
    Route::get("foundperson", "ProfileController@foundperson");
    Route::get("missedperson", "ProfileController@missedperson");
    Route::get("all_notification", "NotificationController@all_notification");
    Route::get("get_notification", "NotificationController@get_notification");
    Route::post('notifcation',"NotificationController@update_notification");
    Route::get('get_post/{id}',"NotificationController@inner_post");
    Route::get('chatroom','ChatController@get_chat_page');
    Route::get('chat/{id}','ChatController@alluser');
    Route::get('chat','ChatController@allmessage');
    Route::post('chat','ChatController@sendmessages');
    Route::get('get_message/{id}','ChatController@create_message');
    Route::get('user','ProfileController@user_info');
    Route::post('user','ProfileController@update_user');
});
Route::get('address/{lat}/{lng}/{lang}',function($lat,$lng,$lang)
    {
      $url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng='.trim($lat).','.trim($lng).'&key=AIzaSyAGmN1GmN4mJz32R_E0oX9qGUc8hlEGT8o&language='.$lang.''.'&sensor=false';
      $json = @file_get_contents($url);
      $data=json_decode($json);
      $status = $data->status;
      if($status=="OK")
      return response()->json(['address' => $data->results[0]->formatted_address]);
      else
      return response()->json(['status' => 'error']);
    });
Route::group(['prefix'=>'/' ,'middleware' => "auth"],function () {
    Route::resource('/','HomeController');
    Route::get('/posts2','HomeController@get_posts');
});
