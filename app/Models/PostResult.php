<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class PostResult extends Model
{
    protected $table = 'post_results';

    protected $fillable = [
        'post_id',
        'result_id'
    ];

    public function post()
    {
        return $this->belongsTo(Post::class, 'post_id', 'id');
    }

    public function resultPost()
    {
        return $this->belongsTo(Post::class, 'result_id', 'id');
    }
}
