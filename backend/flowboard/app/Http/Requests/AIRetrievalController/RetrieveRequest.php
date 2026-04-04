<?php

namespace App\Http\Requests\AIRetrievalController;

use Illuminate\Foundation\Http\FormRequest;

class RetrieveRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'prompt' => ['string', 'required'],
            'type' => ['string', 'required', 'in:collection,workflow']
        ];
    }
}
