<?php


namespace App;

use Illuminate\Database\Eloquent\Model;

class PostImage extends Model
{
  protected $fillable = [
      'Post_id' , 'image'
  ];

  public function Post()
  {
      return $this->belongsTo('App\Post') ;
  }

 //  public function setImageAttribute($value){
 //   $img_name = time().rand(0,999).'.'.$value->getClientOriginalExtension();
 //   $value->move(public_path('front/post_images'),$img_name);
 //   $this->attributes['image']= $img_name ;
 // }
 //
 // public function getImageAttribute($value)
 // {
 //   return url('front/post_images/'.$value);
 // }

 public function user()
 {
     return $this->belongsTo('App\User') ;
 }

 public function post_results()
 {
   return $this->belongsToMany('App\PostImage','post_results','image_id','post_id')
   ->withPivot('id')->withTimestamps();
 }

}
