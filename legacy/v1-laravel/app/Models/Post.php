<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Post extends Model
{
    protected $fillable = [
        "user_id",
        "name",
        "gender",
        "age",
        "birth_date",
        "description",
        "lat",
        "lng",
        "type"
    ];

    public function user()
    {
        return $this->belongsTo(User::class, 'user_id', 'id');
    }

    public function images()
    {
        return $this->hasMany(PostImage::class, 'post_id', 'id');
    }

    public function comments()
    {
        return $this->hasMany(Comment::class, 'post_id', 'id');
    }

    public function likes()
    {
        return $this->hasMany(Like::class, 'post_id', 'id');
    }

    public function results()
    {
        return $this->belongsToMany(Post::class, 'post_results', 'post_id', 'result_id')->withTimestamps();
    }

    public function aiMatches()
    {
        return $this->hasMany(AiMatch::class, 'source_post_id', 'id');
    }

    public function matchedIn()
    {
        return $this->hasMany(AiMatch::class, 'matched_post_id', 'id');
    }
}
