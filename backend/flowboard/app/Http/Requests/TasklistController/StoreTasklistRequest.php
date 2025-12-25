<?php

namespace App\Http\Requests\TasklistController;

use Illuminate\Foundation\Http\FormRequest;

class StoreTasklistRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'name' => ['required', 'string', 'max:255'],
            'workspaceId' => ['required', 'integer', 'exists:workspaces,id'],
        ];
    }
}
