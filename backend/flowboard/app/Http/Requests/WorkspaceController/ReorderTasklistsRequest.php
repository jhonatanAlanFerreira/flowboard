<?php

namespace App\Http\Requests\WorkspaceController;

use Illuminate\Foundation\Http\FormRequest;

class ReorderTasklistsRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'workspaceId' => ['required', 'integer', 'exists:workspaces,id'],
            'order' => ['required', 'array', 'min:1'],
            'order.*' => ['integer', 'exists:tasklists,id'],
        ];
    }
}
