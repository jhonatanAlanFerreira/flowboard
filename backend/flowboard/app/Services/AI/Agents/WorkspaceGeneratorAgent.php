<?php

namespace App\Services\AI\Agents;

use App\Models\AIJob;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class WorkspaceGeneratorAgent
{

    /**
     * Generate workspace from prompt using Python API
     */
    public function generateWorkspace(AIJob $job): array
    {

        try {
            $response = Http::ai()
                ->timeout(10)
                ->post('/generate-workspace', $this->buildPayload($job));

            if ($response->successful()) {
                return $response->json();
            }

            Log::warning('WorkspaceGeneratorAgent failed', [
                'status' => $response->status(),
                'body' => $response->body(),
            ]);
        } catch (\Throwable $e) {
            Log::warning('WorkspaceGeneratorAgent exception', [
                'message' => $e->getMessage(),
            ]);
        }


        Log::error('WorkspaceGeneratorAgent completely unavailable after retries');

        throw new \RuntimeException('AI API is not responding');
    }

    protected function buildPayload(AIJob $job): array
    {
        return [
            'job_id' => $job->id,
            'prompt' => $job->prompt,
        ];
    }
}
