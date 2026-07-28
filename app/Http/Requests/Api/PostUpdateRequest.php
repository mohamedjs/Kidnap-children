<?php

namespace App\Http\Requests\Api;

use Illuminate\Foundation\Http\FormRequest;

class PostUpdateRequest extends FormRequest
{
    public function authorize()
    {
        return true;
    }

    public function rules()
    {
        return [
            'name' => 'sometimes|required|string|max:255',
            'type' => 'sometimes|required|in:founded,missed',
            'gender' => 'nullable|in:male,female',
            'age' => 'nullable|integer|min:0|max:120',
            'birth_date' => 'nullable|date',
            'description' => 'nullable|string',
            'lat' => 'nullable|string',
            'lng' => 'nullable|string',
        ];
    }
}
