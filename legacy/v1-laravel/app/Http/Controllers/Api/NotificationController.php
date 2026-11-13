<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Notification;
use Illuminate\Http\Request;

class NotificationController extends Controller
{
    /**
     * Fetch authenticated user's notifications.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function index(Request $request)
    {
        $notifications = Notification::with('sender')
            ->where('receive_id', $request->user()->id)
            ->orderBy('created_at', 'desc')
            ->paginate(20);

        $unreadCount = Notification::where('receive_id', $request->user()->id)
            ->where('seen', 0)
            ->count();

        return response()->json([
            'unread_count'  => $unreadCount,
            'notifications' => $notifications
        ]);
    }

    /**
     * Mark single notification as read.
     *
     * @param Request $request
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function markAsRead(Request $request, $id)
    {
        $notification = Notification::where('id', $id)
            ->where('receive_id', $request->user()->id)
            ->firstOrFail();

        $notification->update(['seen' => 1]);

        return response()->json([
            'message'      => 'Notification marked as read',
            'notification' => $notification
        ]);
    }

    /**
     * Mark all notifications as read.
     *
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function markAllAsRead(Request $request)
    {
        Notification::where('receive_id', $request->user()->id)
            ->where('seen', 0)
            ->update(['seen' => 1]);

        return response()->json([
            'message' => 'All notifications marked as read'
        ]);
    }
}
