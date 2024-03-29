<?php
namespace App\Events;
use Illuminate\Broadcasting\Channel;
use Illuminate\Queue\SerializesModels;
use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Broadcasting\PresenceChannel;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
class CommentPost implements ShouldBroadcast
{
    use Dispatchable, InteractsWithSockets, SerializesModels;
    public $comment;
    public $message;
    public $key;
    /**
     * Create a new event instance.
     *
     * @return void
     */
    public function __construct($comment,$key)
    {
        $this->comment = $comment;
        $this->key     = $key;
        $this->message = "Comment Your Post";
    }
    /**
     * Get the channels the event should broadcast on.
     *
     * @return \Illuminate\Broadcasting\Channel|array
     */
    public function broadcastOn()
    {
        return new PrivateChannel('comment-post');
    }
    public function broadcastAs()
    {
        return 'comment.created';
    }
}
