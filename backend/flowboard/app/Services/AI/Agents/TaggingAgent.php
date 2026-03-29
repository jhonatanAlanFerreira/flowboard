<?php

namespace App\Services\AI\Agents;

use App\Models\RagChunk;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class TaggingAgent
{
    protected string $endpoint;

    public function __construct()
    {
        $this->endpoint = config('services.ai.endpoint') . '/tagging';
    }

    /**
     * Generate tags from text using Python API
     */
    public function generateTags(RagChunk $chunk): array
    {
        try {
            $response = Http::timeout(10)
                ->post($this->endpoint, $this->buildPayload($chunk));

            if (!$response->successful()) {
                Log::warning('TaggingAgent failed', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                ]);

                return [];
            }

            return $response->json();
        } catch (\Throwable $e) {
            Log::error('TaggingAgent exception', [
                'message' => $e->getMessage(),
            ]);

            return [];
        }
    }

    protected function buildPayload(RagChunk $chunk): array
    {

        return [
            'text' => $chunk->task_description,
            'chunk_id' => $chunk->id
        ];
    }
}
