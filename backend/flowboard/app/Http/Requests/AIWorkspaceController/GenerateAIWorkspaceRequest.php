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
            'prompt' => ['required', 'string', 'min:10', 'max:1000'],
        ];
    }
}
