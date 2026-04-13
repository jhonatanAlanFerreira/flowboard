<?php

namespace App\Services\Chunking;

use App\DTOs\AI\RagChunkDTO;
use App\Enums\RagChunkType;
use App\Models\ChunkTag;
use App\Models\RagChunk;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ChunkService
{

    public function upsertChunk(RagChunkDTO $chunkData): RagChunk
    {

        $conditions = match ($chunkData->type) {
            RagChunkType::TASK => ['type' => $chunkData->type->value, 'task_id' => $chunkData->task_id],
            RagChunkType::LIST => ['type' => $chunkData->type->value, 'tasklist_id' => $chunkData->tasklist_id],
            default => ['type' => $chunkData->type->value, 'workspace_id' => $chunkData->workspace_id],
        };

        return RagChunk::updateOrCreate(
            $conditions,
            [
                'user_id'          => $chunkData->user_id,
                'workspace_id'     => $chunkData->workspace_id,
                'tasklist_id'      => $chunkData->tasklist_id,
                'task_id'          => $chunkData->task_id,
                'content'          => $chunkData->content,
                'task_description' => $chunkData->task_description,
                'metadata'         => $chunkData->metadata,
                'type'             => $chunkData->type->value,
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

    public function createWorkspaceChunks(RagChunk $chunk): void
    {
        $payload = [
            'chunk_id' => $chunk->id,
            'name' => $chunk->content,
            'workspace_id' => $chunk->workspace_id,
            'user_id' => $chunk->user_id,
        ];

        try {
            $response = Http::ai()
                ->timeout(10)
                ->post('/chunks/workspaces', $payload);

            $chunk->markEmbedded();
            $chunk->save();

            if (!$response->successful()) {
                Log::warning('Creating workspace chunks failed', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                    'payload' => $payload,
                ]);
            }
        } catch (\Throwable $e) {
            Log::error('Creating workspace chunks exception', [
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
