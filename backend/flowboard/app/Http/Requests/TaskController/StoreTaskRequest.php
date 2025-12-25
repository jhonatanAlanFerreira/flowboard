<?php

namespace App\Http\Requests\TaskController;

use Illuminate\Foundation\Http\FormRequest;

class StoreTaskRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'description' => ['required', 'string'],
            'tasklistId' => ['required', 'integer', 'exists:tasklists,id'],
        ];
    }
}
