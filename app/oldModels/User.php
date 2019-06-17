<?php

namespace App;

use Illuminate\Notifications\Notifiable;
use Illuminate\Contracts\Auth\MustVerifyEmail;
use Illuminate\Foundation\Auth\User as Authenticatable;

class User extends Authenticatable
{
    use Notifiable;

    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [
        'name' ,'email' ,'phone' , 'password' , 'address' , 'image' ,'background_image','birh_date'
    ];

    /**
     * The attributes that should be hidden for arrays.
     *
     * @var array
     */
    protected $hidden = [
        'password', 'remember_token',
    ];

    public function sender()
    {
      return $this->belongsToMany('App\User','chats','send_id','receive_id')
      ->withPivot('id','message' ,'seen','message_type')->withTimestamps();
    }

    public function receiver()
    {
      return $this->belongsToMany('App\User','chats','receive_id','send_id')
      ->withPivot('id','message' ,'seen','message_type')->withTimestamps();
    }

    public function misses()
    {
      return $this->hasMany('App\Misse','user_id','id');
    }

    public function comments()
    {
      return $this->hasMany('App\Comment','user_id','id');
    }

    public function historys()
    {
      return $this->hasMany('App\History','user_id','id');
    }

    public function region()
    {
        return $this->belongsTo('App\Region') ;
    }

    public function sender_notification()
    {
      return $this->belongsToMany('App\User','notifications','send_id','receive_id')
      ->withPivot('id','title' , 'content' ,'seen')->withTimestamps();
    }

    public function receiver_notification()
    {
      return $this->belongsToMany('App\User','notifications','receive_id','send_id')
      ->withPivot('id','title' , 'content' ,'seen')->withTimestamps();
    }

   //  public function setImageAttribute($value){
   //   $img_name = time().rand(0,999).'.'.$value->getClientOriginalExtension();
   //   $value->move(base_path('front/post_images'),$img_name);
   //   $this->attributes['image']= $img_name ;
   // }
   //
   // public function getImageAttribute($value)
   // {
   //   return url('front/post_images/'.$value);
   // }

}
