<?php

namespace App\Services\Chunking;

use App\Models\ChunkTag;
use App\Models\RagChunk;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ChunkService
{

    public function upsertChunk(array $data): RagChunk
    {
        $conditions = [
            'type' => $data['type'],
        ];

        if ($data['type'] === 'task') {
            $conditions['task_id'] = $data['task_id'];
        } else {
            $conditions['tasklist_id'] = $data['tasklist_id'];
        }

        return RagChunk::updateOrCreate(
            $conditions,
            [
                'user_id' => $data['user_id'],
                'workspace_id' => $data['workspace_id'],
                'tasklist_id' => $data['tasklist_id'] ?? null,
                'task_id' => $data['task_id'] ?? null,
                'content' => $data['content'],
                'task_description' => $data['task_description'] ?? null,
                'metadata' => $data['metadata'] ?? [],
                'type' => $data['type']
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

    public function createListChunks(RagChunk $chunk): void
    {
        $payload = [
            'chunk_id' => $chunk->id,
            'tasklist_id' => $chunk->tasklist_id,
            'content' => $chunk->content,
            'workspace_id' => $chunk->workspace_id,
            'user_id' => $chunk->user_id,
        ];

        try {
            $response = Http::ai()
                ->timeout(10)
                ->post('/chunks/list', $payload);

            $chunk->markEmbedded();
            $chunk->save();

            if (!$response->successful()) {
                Log::warning('Creating list chunks failed', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                    'payload' => $payload,
                ]);
            }
        } catch (\Throwable $e) {
            Log::error('Creating list chunks exception', [
                'message' => $e->getMessage(),
                'payload' => $payload,
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
