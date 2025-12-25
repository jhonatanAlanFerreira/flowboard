<?php

namespace App\Http\Requests\TaskController;

use Illuminate\Foundation\Http\FormRequest;

class UpdateTaskRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'description' => ['sometimes', 'string'],
            'done' => ['sometimes', 'boolean'],
        ];
    }
}
