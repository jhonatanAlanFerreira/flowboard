<?php

namespace App\Services\AI\Retrieval\CollectionWorkspace;

use App\Enums\WorkspaceType;
use App\Services\AI\Retrieval\CollectionWorkspace\DTO\ChunkDTO;
use App\Services\AI\Retrieval\CollectionWorkspace\DTO\TaskListDTO;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class RetrievalCollectionService
{
    public function retrieveLists(string $query, int $userId): array
    {
        try {
            $response = Http::ai()
                ->timeout(10)
                ->post("/retrieval/workspaces-lists", [
                    'query' => $query,
                    'user_id' => $userId,
                    'type' => WorkspaceType::COLLECTION->value,
                ]);

            if (!$response->successful()) {
                Log::warning('RetrievalCollectionService::retrieveLists failed', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                ]);

                return [];
            }

            $data = $response->json();

            return collect($data['lists'] ?? [])->map(function ($list) {
                return new TaskListDTO(
                    tasklist_id: (int) $list['tasklist_id'],
                    score: (float) $list['score'],
                    relevance: (float) $list['relevance'],
                    volume: (int) $list['volume'],
                    concentration: (float) $list['concentration'],
                    volume_norm: (float) $list['volume_norm'],
                    chunks: collect($list['chunks'] ?? [])->map(
                        fn($chunk) =>
                        new ChunkDTO(
                            chunk_id: (int) $chunk['chunk_id'],
                            score: (float) $chunk['score'],
                        )
                    )->toArray()
                );
            })->toArray();
        } catch (\Throwable $e) {
            Log::error('RetrievalCollectionService::retrieveLists exception', [
                'message' => $e->getMessage(),
            ]);

            return [];
        }
    }

    /**
     * @param TaskListDTO[] $tasklists
     */
    public function extractPatternsFromCollectionWorkflow($params)
    {
        try {
            $response = Http::ai()
                ->timeout(10)
                ->post("/retrieval/patterns/extract/collection", $params);

            if (!$response->successful()) {
                Log::warning('RetrievalCollectionService::extractPatterns failed', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                ]);

                return [];
            }

            return $response->json();
        } catch (\Throwable $e) {
            Log::error('RetrievalCollectionService::extractPatterns exception', [
                'message' => $e->getMessage(),
            ]);

            return [];
        }
    }
}
