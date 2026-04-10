<?php

namespace App\Services\AI\Agents;

use App\Models\AIJob;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class SearchStrategistAgent
{

    public function extractSearchIntent(AIJob $job): array
    {
        try {
            $response = Http::ai()->timeout(10)
                ->post('/search_strategist', [
                    'user_id' => $job->user_id,
                    'prompt' => $job->prompt
                ]);

            if (!$response->successful()) {
                Log::warning('Search failed', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                ]);

                return [];
            }

            return $response->json();
        } catch (\Throwable $e) {
            Log::error('Search exception', [
                'message' => $e->getMessage(),
            ]);

            return [];
        }
    }
}
