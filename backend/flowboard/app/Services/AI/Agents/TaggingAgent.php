<?php

namespace App\Services\AI\Agents;

use App\Models\RagChunk;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class TaggingAgent
{

    public function generateTags(RagChunk $chunk): array
    {
        try {
            $response = Http::ai()->timeout(10)
                ->post('/tagging', $this->buildPayload($chunk));

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
            'content' => $chunk->content,
            'chunk_id' => $chunk->id,
            'tasklist_id' => $chunk->tasklist_id,
            'workspace_id' => $chunk->workspace_id,
            'user_id' => $chunk->user_id,
        ];
    }
}
