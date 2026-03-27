<?php

namespace App\Services\AI\Agents;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class WorkspaceGeneratorAgent
{
    protected string $endpoint;

    public function __construct()
    {
        $this->endpoint = config('services.ai.endpoint') . '/generate-workspace';
    }

    /**
     * Generate workspace from prompt using Python API
     */
    public function generateWorkspace(string $prompt): array
    {

        try {
            $response = Http::timeout(10)
                ->post($this->endpoint, $this->buildPayload($prompt));

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

    protected function buildPayload(string $prompt): array
    {
        return [
            'prompt' => $prompt,
        ];
    }
}
