<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Carbon\Carbon;

class Chat extends Model
{
  protected $fillable = [
  'sender_id','reciever_id','message','seen'
  ];

        public function getCreatedAtAttribute($value)
    {
        return Carbon::parse($value)->diffForHumans();
    }

    // echo $dt->toDateString();               // 2015-12-19
    // echo $dt->toFormattedDateString();      // Dec 19, 2015
    // echo $dt->toTimeString();               // 10:10:16
    // echo $dt->toDateTimeString();           // 2015-12-19 10:10:16
    // echo $dt->toDayDateTimeString();
    //echo $dt->diffForHumans($past);

  public function setMessageAttribute($value)
   {

     if(!file_exists($value) || !is_uploaded_file($value)) {
          $this->attributes['message']=$value;
      }
      else {
        $img_name = time().rand(0,999).'.'.$value->getClientOriginalExtension();
        $value->move(base_path('images/chat'),$img_name);
        $this->attributes['message']=$img_name;
      }


   }

   public function getMessageAttribute($value)
    {
      if(strpos( $value, 'png' ) !== false || strpos( $value, 'jpg' ) !== false){
        return  asset('images/chat/'.$value);
      }
        else {
        return $value;
        }

    }
}
