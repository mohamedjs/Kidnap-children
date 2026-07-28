<?php

namespace App\Http\Requests\Api;

use Illuminate\Foundation\Http\FormRequest;

class PostStoreRequest extends FormRequest
{
    public function authorize()
    {
        return true;
    }

    public function rules()
    {
        return [
            'name' => 'required|string|max:255',
            'type' => 'required|in:founded,missed',
            'gender' => 'nullable|in:male,female',
            'age' => 'nullable|integer|min:0|max:120',
            'birth_date' => 'nullable|date',
            'description' => 'nullable|string',
            'lat' => 'nullable|string',
            'lng' => 'nullable|string',
            'images' => 'nullable|array',
            'images.*' => 'nullable|image|mimes:jpeg,png,jpg,gif|max:5120',
        ];
    }
}
