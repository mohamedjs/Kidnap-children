<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Comment extends Model
{
  protected $fillable = [
      'user_id' , 'comment' ,  'image'  ,'post_id'
  ];

  public function user()
  {
      return $this->belongsTo('App\User') ;
  }


  public function Post()
  {
      return $this->belongsTo('App\Post') ;
  }


  public function setImageAttribute($value){
   $img_name = time().rand(0,999).'.'.$value->getClientOriginalExtension();
   $value->move(public_path('finder_image'),$img_name);
   $this->attributes['image']= $img_name ;
 }

 public function getImageAttribute($value)
 {
   return url('finder_image/'.$value);
 }
}
