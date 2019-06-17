<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use App\Models\User;

class Post extends Model
{

    protected $fillable = [
        "name",
        "birth_date",
        "description",
        "type",
        "gender",
        "age",
        "lat",
        "lng",
        "user_id"
    ];
    public function images()
    {
        return $this->hasMany(PostImage::class);
    }

    public function user()
    {
        return $this->belongsTo(User::class, 'user_id', "id");
    }

    public function comments()
    {
        return $this->hasMany(Comment::class);
    }

    public function posts()
    {
      return $this->belongsToMany('App\Models\Post','post_results','result_id','post_id')
      ->withPivot('id')->withTimestamps();
     }

    public function results()
    {
      return $this->belongsToMany('App\Models\Post','post_results','post_id','result_id')
      ->withPivot('id')->withTimestamps();
    }
}
