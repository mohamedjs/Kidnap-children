<?php

namespace App\Models;

use Illuminate\Notifications\Notifiable;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Laravel\Passport\HasApiTokens;

class User extends Authenticatable
{
    use HasApiTokens, Notifiable;

    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [
        'name',
        'email',
        'phone',
        'password',
        'address',
        'gender',
        'birth_date',
        'image',
        'background_image'
    ];

    /**
     * The attributes that should be hidden for arrays.
     *
     * @var array
     */
    protected $hidden = [
        'password',
        'remember_token',
    ];

    public function posts()
    {
        return $this->hasMany(Post::class, 'user_id', 'id');
    }

    public function comments()
    {
        return $this->hasMany(Comment::class, 'user_id', 'id');
    }

    public function likes()
    {
        return $this->hasMany(Like::class, 'user_id', 'id');
    }

    public function sentMessages()
    {
        return $this->hasMany(Chat::class, 'sender_id', 'id');
    }

    public function receivedMessages()
    {
        return $this->hasMany(Chat::class, 'reciever_id', 'id');
    }

    public function sentNotifications()
    {
        return $this->hasMany(Notification::class, 'send_id', 'id');
    }

    public function receivedNotifications()
    {
        return $this->hasMany(Notification::class, 'receive_id', 'id');
    }
}
