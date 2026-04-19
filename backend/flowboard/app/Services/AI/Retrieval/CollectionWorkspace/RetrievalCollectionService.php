<?php

namespace App\Services\AI\Retrieval\CollectionWorkspace;

use App\DTOs\AI\ChunkDTO;
use App\DTOs\AI\ExtractPatternsResponseDTO;
use App\DTOs\AI\PatternDTO;
use App\DTOs\AI\TaskListDTO;
use App\DTOs\AI\TaskListPatternsDTO;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class RetrievalCollectionService
{
    /**
     * @return TaskListDTO[]
     */
    public function retrieveLists(string $query, int $userId, ?array $workspaceIds = null): array
    {
        try {
            $payload = [
                'query' => $query,
                'user_id' => $userId,
            ];

            if ($workspaceIds) {
                $payload['workspace_ids'] = $workspaceIds;
            }

            $response = Http::ai()
                ->timeout(10)
                ->post("/retrieval/collection/workspaces-lists", $payload);

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
     * @param array<int, TaskListDTO> $workspaceLists
     * @return ExtractPatternsResponseDTO
     */
    public function extractPatternsFromCollectionWorkspace($workspaceLists)
    {
        try {
            $response = Http::ai()
                ->timeout(10)
                ->post("/retrieval/patterns/extract/collection", $workspaceLists);

            if (!$response->successful()) {
                Log::warning('RetrievalCollectionService::extractPatterns failed', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                ]);

                return [];
            }

            $data = $response->json();

            $results = array_map(function (array $result) {

                $patterns = array_map(function (array $pattern) {
                    return new PatternDTO(
                        tag: (string) $pattern['tag'],
                        score: (float) $pattern['score'],
                        task: (string) $pattern['task']
                    );
                }, $result['patterns'] ?? []);

                return new TaskListPatternsDTO(
                    tasklist_id: (int) $result['tasklist_id'],
                    patterns: $patterns
                );
            }, $data['results'] ?? []);

            return new ExtractPatternsResponseDTO($results);
        } catch (\Throwable $e) {
            Log::error('RetrievalCollectionService::extractPatterns exception', [
                'message' => $e->getMessage(),
            ]);

            return [];
        }
    }
}
