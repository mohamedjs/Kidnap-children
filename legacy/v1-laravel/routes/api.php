<?php

use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| REST API Routes
|--------------------------------------------------------------------------
*/

Route::group(['namespace' => 'Api'], function () {

    // Auth Public Endpoints
    Route::get('/health', function () {
        return response()->json(['status' => 'ok', 'service' => 'laravel-api']);
    });
    Route::post('/auth/register', 'AuthController@register');
    Route::post('/auth/login', 'AuthController@login');

    // Public Posts & Search
    Route::get('/posts', 'PostController@index');
    Route::get('/posts/{id}', 'PostController@show');
    Route::get('/posts/{postId}/comments', 'CommentController@index');
    Route::get('/posts/{postId}/likes', 'LikeController@index');
    Route::get('/search', 'SearchController@search');

    // Public Profile
    Route::get('/profile/{id}', 'ProfileController@show');

    // Authenticated API Routes
    Route::group(['middleware' => 'auth:api'], function () {
        // Auth
        Route::post('/auth/logout', 'AuthController@logout');
        Route::get('/auth/me', 'AuthController@me');

        // Profile
        Route::put('/profile', 'ProfileController@update');
        Route::post('/profile/image', 'ProfileController@uploadImage');

        // Posts
        Route::post('/posts', 'PostController@store');
        Route::put('/posts/{id}', 'PostController@update');
        Route::delete('/posts/{id}', 'PostController@destroy');
        Route::post('/posts/{id}/images', 'PostController@uploadImages');

        // Comments
        Route::post('/posts/{postId}/comments', 'CommentController@store');
        Route::delete('/comments/{id}', 'CommentController@destroy');

        // Likes
        Route::post('/posts/{postId}/like', 'LikeController@toggle');

        // Private Messaging
        Route::get('/messages/conversations', 'MessageController@conversations');
        Route::get('/messages/{recipientId}', 'MessageController@index');
        Route::post('/messages', 'MessageController@store');
        Route::post('/messages/{id}/read', 'MessageController@markAsRead');

        // Notifications
        Route::get('/notifications', 'NotificationController@index');
        Route::post('/notifications/{id}/read', 'NotificationController@markAsRead');
        Route::post('/notifications/read-all', 'NotificationController@markAllAsRead');

        // AI Matches
        Route::get('/matches', 'AiMatchController@index');
        Route::get('/posts/{id}/matches', 'AiMatchController@showForPost');
        Route::post('/posts/{id}/process-ai', 'AiMatchController@processPost');
    });
});
