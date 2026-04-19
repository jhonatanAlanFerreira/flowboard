<?php

namespace App\Http\Requests\AIWorkspaceController;

use Illuminate\Foundation\Http\FormRequest;

class GenerateAIWorkspaceRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'prompt' => ['required', 'string'],
            'type' => ['required', 'string', 'in:collection_workspace,workflow_workspace,user_question'],
            'workspace_category_id' => ['nullable', 'integer']
        ];
    }
}
