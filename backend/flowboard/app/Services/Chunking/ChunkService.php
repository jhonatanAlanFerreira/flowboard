<?php

namespace App\Services\Chunking;

use App\Models\ChunkTag;
use App\Models\RagChunk;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ChunkService
{

    public function upsertTaskChunk(int $taskId, array $data): RagChunk
    {
        return RagChunk::updateOrCreate(
            [
                'task_id' => $taskId,
            ],
            [
                'user_id' => $data['user_id'],
                'workspace_id' => $data['workspace_id'],
                'tasklist_id' => $data['tasklist_id'],
                'content' => $data['content'],
                'task_description' => $data['task_description'],
                'metadata' => $data['metadata'] ?? [],
            ]
        );
    }


    public function deleteTaskChunk(int $chunkId): void
    {
        try {
            $response = Http::ai()
                ->timeout(10)
                ->delete("/chunks/" . $chunkId);

            if (!$response->successful()) {
                Log::warning('Deleting failed', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                ]);
            }
        } catch (\Throwable $e) {
            Log::error('Deleting exception', [
                'message' => $e->getMessage(),
            ]);
        }
    }

    public function deleteTaskChunksFromList(int $tasklistId): void
    {
        try {
            $response = Http::ai()
                ->timeout(10)
                ->delete("/chunks/tasklist/" . $tasklistId);

            if (!$response->successful()) {
                Log::warning('Deleting failed', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                ]);
            }
        } catch (\Throwable $e) {
            Log::error('Deleting exception', [
                'message' => $e->getMessage(),
            ]);
        }
    }

    public function deleteTaskChunksFromWorkspace(int $workspaceId): void
    {
        try {
            $response = Http::ai()
                ->timeout(10)
                ->delete("/chunks/workspace/" . $workspaceId);

            if (!$response->successful()) {
                Log::warning('Deleting failed', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                ]);
            }
        } catch (\Throwable $e) {
            Log::error('Deleting exception', [
                'message' => $e->getMessage(),
            ]);
        }
    }


    public function updateChunkTags(int $chunkId, array $params): void
    {
        $chunk = RagChunk::findOrFail($chunkId);

        $metadata = $chunk->metadata ?? [];

        $tags = $params['tags'];

        $metadata['tags'] = $tags;

        $chunk->metadata = $metadata;
        $chunk->markEmbedded();
        $chunk->save();

        $tags = array_map(fn($tag) => ['name' => $tag], $tags);
        ChunkTag::upsert($tags, ['name']);
    }
}
