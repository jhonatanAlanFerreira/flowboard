<?php

namespace App\Services\AI\Agents;

use App\Models\AIJob;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class GenerateAnswerAgent
{

    public function generateAnswer($chunks, int $jobId): array
    {
        try {
            $response = Http::ai()->timeout(10)
                ->post('/search_strategist/process-answer', [
                    "ai_job_id" => $jobId,
                    "prompt" => AIJob::find($jobId)->prompt,
                    "chunks" => $chunks
                ]);

            if (!$response->successful()) {
                Log::warning('Generate answer failed', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                ]);

                return [];
            }

            return $response->json();
        } catch (\Throwable $e) {
            Log::error('Generate answer exception', [
                'message' => $e->getMessage(),
            ]);

            return [];
        }
    }
}
