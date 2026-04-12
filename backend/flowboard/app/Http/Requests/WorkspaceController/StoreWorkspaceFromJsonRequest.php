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
            'workspace' => ['required', 'array'],
            'workspace.name' => ['required', 'string', 'max:255'],
            'workspace.lists' => ['required', 'array', 'min:1'],
            'workspace.lists.*.name' => ['required', 'string', 'max:255'],
            'workspace.lists.*.tasks' => ['required', 'array', 'min:1'],
            'workspace.lists.*.tasks.*.description' => ['required', 'string', 'max:1000'],
        ];
    }
}
