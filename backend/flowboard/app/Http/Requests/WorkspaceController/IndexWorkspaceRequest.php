<?php

namespace App\Http\Requests\WorkspaceController;

use Illuminate\Foundation\Http\FormRequest;

class IndexWorkspaceRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'workspaceId' => ['required', 'integer', 'exists:workspaces,id'],
        ];
    }

    protected function prepareForValidation()
    {
        $this->merge([
            'workspaceId' => $this->route('workspaceId'),
        ]);
    }
}
