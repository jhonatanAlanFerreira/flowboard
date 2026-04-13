<?php

namespace App\Services\AI\Retrieval\WorkflowWorkspace;

use App\DTOs\AI\WorkspaceDTO;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class RetrievalWorkflowService
{
    public function retrieveLists(string $query, int $userId): array
    {
        try {
            $response = Http::ai()
                ->timeout(10)
                ->post("/retrieval/workflow/workspaces", [
                    'query' => $query,
                    'user_id' => $userId,
                ]);

            if (!$response->successful()) {
                Log::warning('RetrievalWorkflowService::retrieveLists failed', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                ]);

                return [];
            }

            $data = $response->json();

            return collect($data['workspaces'] ?? [])->map(function ($data) {
                return new WorkspaceDTO(
                    workspace_id: (string) $data['workspace_id'],
                    score: (float)  $data['score'],
                    max_score: (float)  $data['max_score'],
                    match_count: (int)    $data['match_count'],
                    chunk_id: (string) $data['chunk_id'],
                    final_score: (float)  $data['final_score'],
                );
            })->toArray();
        } catch (\Throwable $e) {
            Log::error('RetrievalWorkflowService::retrieveLists exception', [
                'message' => $e->getMessage(),
            ]);

            return [];
        }
    }
}
