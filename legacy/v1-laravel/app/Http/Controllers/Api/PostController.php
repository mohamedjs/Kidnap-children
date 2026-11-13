<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\PostStoreRequest;
use App\Http\Requests\Api\PostUpdateRequest;
use App\Models\Post;
use App\Models\PostImage;
use Illuminate\Http\Request;

class PostController extends Controller
{
    public function index(Request $request)
    {
        $query = Post::with(['user', 'images', 'comments.user'])->withCount('likes');

        if ($request->has('type') && in_array($request->type, ['founded', 'missed'])) {
            $query->where('type', $request->type);
        }

        if ($request->has('gender') && in_array($request->gender, ['male', 'female'])) {
            $query->where('gender', $request->gender);
        }

        if ($request->filled('age')) {
            $query->where('age', $request->age);
        }

        if ($request->filled('query')) {
            $searchTerm = '%' . $request->query('query') . '%';
            $query->where(function ($q) use ($searchTerm) {
                $q->where('name', 'like', $searchTerm)
                  ->orWhere('description', 'like', $searchTerm);
            });
        }

        $posts = $query->orderBy('created_at', 'desc')->paginate(15);

        return response()->json($posts);
    }

    public function store(PostStoreRequest $request)
    {
        $user = $request->user();

        $post = Post::create([
            'user_id' => $user->id,
            'name' => $request->name,
            'type' => $request->type,
            'gender' => $request->gender ?? 'male',
            'age' => $request->age,
            'birth_date' => $request->birth_date,
            'description' => $request->description,
            'lat' => $request->lat,
            'lng' => $request->lng,
        ]);

        if ($request->hasFile('images')) {
            foreach ($request->file('images') as $file) {
                $filename = time() . '_' . uniqid() . '.' . $file->getClientOriginalExtension();
                $file->move(public_path('uploads/posts'), $filename);
                PostImage::create([
                    'post_id' => $post->id,
                    'image' => 'uploads/posts/' . $filename
                ]);
            }
            \App\Jobs\ProcessImageWithAIService::dispatch($post);
        }

        $post->load(['user', 'images']);

        return response()->json([
            'message' => 'Post created successfully',
            'post' => $post
        ], 201);
    }

    public function show($id)
    {
        $post = Post::with(['user', 'images', 'comments.user'])->withCount('likes')->findOrFail($id);
        return response()->json(['post' => $post]);
    }

    public function update(PostUpdateRequest $request, $id)
    {
        $post = Post::findOrFail($id);
        $this->authorize('update', $post);

        $post->update($request->only([
            'name', 'type', 'gender', 'age', 'birth_date', 'description', 'lat', 'lng'
        ]));

        return response()->json([
            'message' => 'Post updated successfully',
            'post' => $post->fresh(['user', 'images'])
        ]);
    }

    public function destroy(Request $request, $id)
    {
        $post = Post::findOrFail($id);
        $this->authorize('delete', $post);

        $post->delete();

        return response()->json([
            'message' => 'Post deleted successfully'
        ]);
    }

    public function uploadImages(Request $request, $id)
    {
        $post = Post::findOrFail($id);
        $this->authorize('update', $post);

        $request->validate([
            'images' => 'required|array',
            'images.*' => 'image|mimes:jpeg,png,jpg,gif|max:5120',
        ]);

        $uploadedImages = [];
        foreach ($request->file('images') as $file) {
            $filename = time() . '_' . uniqid() . '.' . $file->getClientOriginalExtension();
            $file->move(public_path('uploads/posts'), $filename);
            $img = PostImage::create([
                'post_id' => $post->id,
                'image' => 'uploads/posts/' . $filename
            ]);
            $uploadedImages[] = $img;
        }

        if (!empty($uploadedImages)) {
            \App\Jobs\ProcessImageWithAIService::dispatch($post);
        }

        return response()->json([
            'message' => 'Images uploaded successfully',
            'images' => $uploadedImages
        ]);
    }
}
