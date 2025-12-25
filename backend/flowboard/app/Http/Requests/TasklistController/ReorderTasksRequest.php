<?php

namespace App\Http\Requests\TasklistController;

use Illuminate\Foundation\Http\FormRequest;

class ReorderTasksRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'newTasklistId' => ['required', 'integer', 'exists:tasklists,id'],
            'sourceTasklistId' => ['required', 'integer', 'exists:tasklists,id'],
            'order' => ['required', 'array', 'min:1'],
            'order.*' => ['integer', 'exists:tasks,id'],
        ];
    }
}
