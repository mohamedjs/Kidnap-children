<?php

namespace App\Http\Controllers\Api;

use App\Events\ChatMessageSent;
use App\Http\Controllers\Controller;
use App\Models\Chat;
use App\Models\Notification;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class MessageController extends Controller
{
    /**
     * Get list of conversations for authenticated user.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function conversations(Request $request)
    {
        $userId = $request->user()->id;

        // Get user IDs with whom authenticated user has exchanged messages
        $contactIds = Chat::where('sender_id', $userId)
            ->orWhere('reciever_id', $userId)
            ->select(DB::raw("IF(sender_id = {$userId}, reciever_id, sender_id) as contact_id"))
            ->distinct()
            ->pluck('contact_id');

        $conversations = [];
        foreach ($contactIds as $contactId) {
            $user = User::find($contactId);
            if (!$user) {
                continue;
            }

            $lastMessage = Chat::where(function ($q) use ($userId, $contactId) {
                $q->where('sender_id', $userId)->where('reciever_id', $contactId);
            })->orWhere(function ($q) use ($userId, $contactId) {
                $q->where('sender_id', $contactId)->where('reciever_id', $userId);
            })->orderBy('created_at', 'desc')->first();

            $unreadCount = Chat::where('sender_id', $contactId)
                ->where('reciever_id', $userId)
                ->where('seen', 0)
                ->count();

            $conversations[] = [
                'user'         => $user,
                'last_message' => $lastMessage,
                'unread_count' => $unreadCount,
            ];
        }

        return response()->json([
            'conversations' => $conversations
        ]);
    }

    /**
     * Get messages exchanged with a specific recipient.
     *
     * @param Request $request
     * @param int $recipientId
     * @return \Illuminate\Http\JsonResponse
     */
    public function index(Request $request, $recipientId)
    {
        $userId = $request->user()->id;

        User::findOrFail($recipientId);

        // Mark incoming messages from this sender as seen
        Chat::where('sender_id', $recipientId)
            ->where('reciever_id', $userId)
            ->where('seen', 0)
            ->update(['seen' => 1]);

        $messages = Chat::where(function ($q) use ($userId, $recipientId) {
            $q->where('sender_id', $userId)->where('reciever_id', $recipientId);
        })->orWhere(function ($q) use ($userId, $recipientId) {
            $q->where('sender_id', $recipientId)->where('reciever_id', $userId);
        })->orderBy('created_at', 'asc')->get();

        return response()->json([
            'recipient_id' => (int) $recipientId,
            'messages'     => $messages
        ]);
    }

    /**
     * Send a private message.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function store(Request $request)
    {
        $request->validate([
            'reciever_id' => 'required|integer|exists:users,id',
            'message'     => 'required|string|max:5000',
        ]);

        $sender = $request->user();
        $recipientId = (int) $request->reciever_id;

        if ($sender->id === $recipientId) {
            return response()->json([
                'message' => 'Cannot send message to yourself'
            ], 422);
        }

        $chat = Chat::create([
            'sender_id'   => $sender->id,
            'reciever_id' => $recipientId,
            'message'     => $request->message,
            'seen'        => 0,
        ]);

        // Create DB notification for recipient
        Notification::create([
            'send_id'          => $sender->id,
            'receive_id'       => $recipientId,
            'title'            => 'New Private Message',
            'content'          => "{$sender->name} sent you a message: " . substr($request->message, 0, 50),
            'notification_url' => "/api/messages/{$sender->id}",
            'type'             => 'chat',
            'seen'             => 0,
        ]);

        // Dispatch real-time broadcast event
        event(new ChatMessageSent($chat));

        return response()->json([
            'message' => 'Message sent successfully',
            'chat'    => $chat
        ], 201);
    }

    /**
     * Mark a message as read.
     *
     * @param Request $request
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function markAsRead(Request $request, $id)
    {
        $chat = Chat::where('id', $id)
            ->where('reciever_id', $request->user()->id)
            ->firstOrFail();

        $chat->update(['seen' => 1]);

        return response()->json([
            'message' => 'Message marked as read',
            'chat'    => $chat
        ]);
    }
}
