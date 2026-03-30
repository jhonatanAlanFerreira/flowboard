<?php

namespace App\Http\Requests\AIChunkController;

use Illuminate\Foundation\Http\FormRequest;

class UpdateChunkTagsRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'tags' => ['array'],
        ];
    }
}
