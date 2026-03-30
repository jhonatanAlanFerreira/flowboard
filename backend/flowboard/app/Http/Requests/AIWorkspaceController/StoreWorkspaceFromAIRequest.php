<?php

namespace App\Http\Requests\AIWorkspaceController;

use Illuminate\Foundation\Http\FormRequest;

class StoreWorkspaceFromAIRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'job_id' => ['required', 'integer'],
            'workflow' => ['required', 'array'],
            'workflow.name' => ['required', 'string', 'max:255'],
            'workflow.lists' => ['required', 'array', 'min:1'],
            'workflow.lists.*.name' => ['required', 'string', 'max:255'],
            'workflow.lists.*.tasks' => ['required', 'array', 'min:1'],
            'workflow.lists.*.tasks.*.description' => ['required', 'string', 'max:1000'],
        ];
    }
}
