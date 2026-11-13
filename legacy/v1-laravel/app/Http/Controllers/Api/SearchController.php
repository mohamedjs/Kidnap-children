<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Post;
use Illuminate\Http\Request;

class SearchController extends Controller
{
    public function search(Request $request)
    {
        $query = Post::with(['user', 'images'])->withCount('likes');

        if ($request->filled('query')) {
            $searchTerm = '%' . $request->query('query') . '%';
            $query->where(function ($q) use ($searchTerm) {
                $q->where('name', 'like', $searchTerm)
                  ->orWhere('description', 'like', $searchTerm);
            });
        }

        if ($request->filled('type') && in_array($request->type, ['founded', 'missed'])) {
            $query->where('type', $request->type);
        }

        if ($request->filled('gender') && in_array($request->gender, ['male', 'female'])) {
            $query->where('gender', $request->gender);
        }

        if ($request->filled('age')) {
            $query->where('age', $request->age);
        }

        $results = $query->orderBy('created_at', 'desc')->paginate(15);

        return response()->json($results);
    }
}
