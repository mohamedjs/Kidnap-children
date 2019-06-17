<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Post extends Model
{
    protected $fillable = [
        'user_id', 'name', 'birth_date', 'desc', 'region_id', 'gender', 'lat', 'lang', 'found', 'age', 'type'
    ];

    public function user()
    {
        return $this->belongsTo('App\User');
    }

    public function region()
    {
        return $this->belongsTo('App\Region');
    }

    public function images()
    {
        return $this->hasMany('App\PostImage', 'post_id', 'id');
    }

    public function comments()
    {
        return $this->hasMany('App\Comment', 'post_id', 'id');
    }

    public function likes()
    {
        return $this->hasMany('App\Like', 'post_id', 'id');
    }

    public function results()
    {
        return $this->belongsToMany('App\PostImage', 'post_results', 'post_id', 'image_id')
            ->withPivot('id')->withTimestamps();
    }
}
