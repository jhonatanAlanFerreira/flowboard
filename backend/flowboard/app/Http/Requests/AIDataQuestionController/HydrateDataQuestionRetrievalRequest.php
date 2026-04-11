<?php

namespace App\Http\Requests\AIDataQuestionController;

use Illuminate\Foundation\Http\FormRequest;

class HydrateDataQuestionRetrievalRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            '*' => 'required|array',
            '*.chunk_id' => 'required|string',
            '*.workspace_id' => 'required|string',
            '*.tasklist_id' => 'nullable|string',
            '*.content' => 'required|string',
            '*.search_score' => 'required|numeric',
            '*.found_in_both' => 'required|boolean',
        ];
    }
}
