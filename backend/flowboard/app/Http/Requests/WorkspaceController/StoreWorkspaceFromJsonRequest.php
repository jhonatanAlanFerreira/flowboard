<?php

namespace App\Http\Requests\WorkspaceController;

use Illuminate\Foundation\Http\FormRequest;

class StoreWorkspaceFromJsonRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'workflow' => ['required', 'array'],
            'workflow.name' => ['required', 'string', 'max:255'],
            'workflow.lists' => ['required', 'array', 'min:1'],
            'workflow.lists.*.name' => ['required', 'string', 'max:255'],
            'workflow.lists.*.tasks' => ['required', 'array', 'min:1'],
            'workflow.lists.*.tasks.*.description' => ['required', 'string', 'max:1000'],
        ];
    }
}