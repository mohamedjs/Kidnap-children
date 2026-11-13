<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\Request;

class ProfileController extends Controller
{
    public function show($id)
    {
        $user = User::withCount(['posts', 'comments'])->findOrFail($id);
        return response()->json(['user' => $user]);
    }

    public function update(Request $request)
    {
        $user = $request->user();

        $request->validate([
            'name' => 'sometimes|required|string|max:255',
            'phone' => 'nullable|string|max:50',
            'address' => 'nullable|string|max:255',
            'gender' => 'nullable|in:male,female',
            'birth_date' => 'nullable|date',
        ]);

        $user->update($request->only(['name', 'phone', 'address', 'gender', 'birth_date']));

        return response()->json([
            'message' => 'Profile updated successfully',
            'user' => $user
        ]);
    }

    public function uploadImage(Request $request)
    {
        $request->validate([
            'image' => 'required|image|mimes:jpeg,png,jpg,gif|max:5120',
        ]);

        $user = $request->user();

        if ($request->hasFile('image')) {
            $file = $request->file('image');
            $filename = time() . '_' . uniqid() . '.' . $file->getClientOriginalExtension();
            $file->move(public_path('uploads/users'), $filename);
            $user->image = 'uploads/users/' . $filename;
            $user->save();
        }

        return response()->json([
            'message' => 'Profile image uploaded successfully',
            'user' => $user
        ]);
    }
}
