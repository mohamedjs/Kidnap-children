<?php

namespace App\Events;

use App\Models\AiMatch;
use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Contracts\Broadcasting\ShouldBroadcastNow;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class AiMatchFound implements ShouldBroadcastNow
{
    use Dispatchable, SerializesModels;

    public $aiMatch;
    public $recipientId;
    public $message;

    /**
     * Create a new event instance.
     *
     * @param AiMatch $aiMatch
     * @param int $recipientId
     * @param string $message
     */
    public function __construct(AiMatch $aiMatch, int $recipientId, string $message)
    {
        $this->aiMatch = $aiMatch;
        $this->recipientId = $recipientId;
        $this->message = $message;
    }

    /**
     * Get the channels the event should broadcast on.
     *
     * @return array
     */
    public function broadcastOn()
    {
        return [
            new PrivateChannel('notification.' . $this->recipientId),
        ];
    }

    /**
     * The event's broadcast name.
     *
     * @return string
     */
    public function broadcastAs()
    {
        return 'ai.match.found';
    }
}
