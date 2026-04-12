<?php

namespace App\Http\Requests\AIDataQuestionController;

use Illuminate\Foundation\Http\FormRequest;

class DataQuestionCompleteRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'markdown_answer' => 'required|string',
            'citations' => 'required|array',
            'citations.*' => 'required|string',
        ];
    }
}
