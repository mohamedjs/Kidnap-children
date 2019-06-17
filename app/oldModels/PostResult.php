<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class PostResult extends Model
{
  protected $fillable = [
      'image_id'  ,'post_id'
  ];

  public function images()
  {
      return $this->belongsTo('App\PostImage') ;
  }


  public function Post()
  {
      return $this->belongsTo('App\Post') ;
  }
}
