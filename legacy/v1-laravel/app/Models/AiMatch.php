<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class AiMatch extends Model
{
    protected $table = 'ai_matches';

    protected $fillable = [
        'source_post_id',
        'matched_post_id',
        'confidence',
        'face_detected',
        'status',
        'raw_response',
    ];

    protected $casts = [
        'confidence' => 'float',
        'face_detected' => 'boolean',
    ];

    public function sourcePost()
    {
        return $this->belongsTo(Post::class, 'source_post_id', 'id');
    }

    public function matchedPost()
    {
        return $this->belongsTo(Post::class, 'matched_post_id', 'id');
    }
}
