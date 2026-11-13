<?php


namespace App\Http\Controllers\Frontend;


use Illuminate\Http\Request;

use App\Models\User;
use App\Models\Chat;
use App\PushNotification;
use DB;
use App\Http\Controllers\Controller;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\File;
use Carbon\Carbon;
use App\Events\SendMessage;
class ChatController extends Controller

{
  public function get_chat_page()
  {
    return view('front.chat');
  }

  public function create_message($id)
  {
    $message=Chat::create([
      'sender_id' =>  \Auth::id(),
      'reciever_id' =>  $id,
      'seen' => 1,
      'message' => 'new message'
    ]);
    return view('front.chat');
  }

  public function sendmessages(Request $request)
  {

        $message=Chat::create([
          'sender_id' =>  $request->sender_id,
          'reciever_id' =>  $request->reciever_id,
          'seen' => 1,
          'message' => $request->message
        ]);

      if( strpos( $message->message, 'images/chat' ) !== false){
         $message['image']=1;
       }
       else {
         $message['image']=0;
       }
      broadcast(new SendMessage('send message',$request->reciever_id))->toOthers();
      return response()->json(['status' => 'success','data' => $message]);

  }

  public function allmessage(Request $request)
  {
    $send_id=$request->send_id;
    $recieve_id=$request->recieve_id;
    $all=Chat::join('users as sender','chats.sender_id','=','sender.id')->
               join('users as recieve','chats.reciever_id','=','recieve.id')->
               select('chats.id as chat_id','sender.name as sender_name','recieve.name as reciever_name',
               'sender.id as sender_id','recieve.id as reciever_id','chats.message','chats.created_at as created_at')->
               where('chats.sender_id',$request->send_id)->where('chats.reciever_id',$request->recieve_id)
               ->orwhere(function ($query) use ($send_id,$recieve_id)  {
                $query->where('chats.sender_id',$recieve_id)->
                        where('chats.reciever_id',$send_id);
                })
               ->orderBy('chats.created_at','asc')->get();
    $user_info = User::find($recieve_id);
    return response()->json(['all' => $all , 'user_info' => $user_info]);
    //dd($all);die;
  }

  public function alluser($id)
  {

    $users=Chat::select('chats.sender_id','chats.reciever_id','chats.message','chats.created_at','chats.seen')->
              join(DB::raw('(
                  SELECT
                      LEAST(sender_id, reciever_id) AS sender_id,
                      GREATEST(sender_id, reciever_id) AS reciever_id,
                      MAX(id) AS max_id
                  FROM chats
                  GROUP BY
                      LEAST(sender_id, reciever_id),
                      GREATEST(sender_id, reciever_id)
              ) AS t2'),function($join){
                  $join->on(DB::raw('LEAST(chats.sender_id, chats.reciever_id)'), '=','t2.sender_id'); // i want to join the users table with either of these columns
                  $join->On(DB::raw('GREATEST(chats.sender_id, chats.reciever_id)'),'=','t2.reciever_id');
                  $join->On(DB::raw('chats.id '),'=', 't2.max_id');
              })->where('chats.sender_id',$id)->orwhere('chats.reciever_id',$id)->orderBy('created_at','desc')->get();
    //dd($users);die;
    $messages=[];
    $all=[];
    foreach ($users as $user) {

      if( $user->sender_id==$id){

        $recie=User::whereId($user->reciever_id)->first();
        $success['user_name']=$recie->name;
        $success['user_id']=$user->reciever_id;
        $success['user_image'] = $recie->image;
        $success['seen']=1;
        $success['message']=$user->message;
        $success['created_at']=$user->created_at;
        array_push($messages,$success);
      }

      else if($user->reciever_id==$id){
        $recie=User::whereId($user->sender_id)->first();
        $success['user_name']=$recie->name;
        $success['user_id']=$user->sender_id;
        $success['user_image'] = $recie->image;
        $success['seen']=$user->seen;
        $success['message']=$user->message;
        $success['created_at']=$user->created_at;
        array_push($messages,$success);
      }
    }

    foreach ($messages as $msg) {
        array_push($all,$msg);
    }
    return $all;

  }

  public static function count_seen($id)
  {
    $count = Chat::where('sender_id', '!=', 1)->where('reciever_id',$id)->where('seen',0)->count();
    return $count;

   }


}
