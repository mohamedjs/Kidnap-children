<?php

namespace App\Events;

use Illuminate\Broadcasting\Channel;
use Illuminate\Queue\SerializesModels;
use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Broadcasting\PresenceChannel;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;

class LikePost implements ShouldBroadcast
{
    use Dispatchable, InteractsWithSockets, SerializesModels;
    public $like;
    public $message;
    /**
     * Create a new event instance.
     *
     * @return void
     */
    public function __construct($like)
    {
        $this->like     = $like;
        $this->message = "{$like->user->name} Like Your Post";
    }

    /**
     * Get the channels the event should broadcast on.
     *
     * @return \Illuminate\Broadcasting\Channel|array
     */
    public function broadcastOn()
    {
        return new Channel('like-post');
    }

    // public function broadcastWith()
    // {
    //   return [
    //     'like' => $this->like,
    //     'message' => $this->like->user->name." Like Your Post"
    //   ];
    // }
}
