<?php

namespace App\Services\Chunking;

use App\Models\ChunkTag;
use App\Models\RagChunk;
use Illuminate\Support\Collection;

class ChunkService
{

    public function upsertTaskChunk(int $taskId, array $data): RagChunk
    {
        return RagChunk::updateOrCreate(
            [
                'type' => 'task',
                'task_id' => $taskId,
            ],
            [
                'user_id' => $data['user_id'],
                'workspace_id' => $data['workspace_id'],
                'tasklist_id' => $data['tasklist_id'],
                'content' => $data['content'],
                'metadata' => $data['metadata'] ?? [],
            ]
        );
    }


    public function deleteTaskChunk(int $taskId): void
    {
        RagChunk::where('type', 'task')
            ->where('reference_id', $taskId)
            ->delete();
    }


    public function getTaskChunksByList(int $listId): Collection
    {
        return RagChunk::where('type', 'task')
            ->where('list_id', $listId)
            ->get();
    }


    public function upsertListPatternChunk(int $listId, int $workspaceId, array $data): RagChunk
    {
        return RagChunk::updateOrCreate(
            [
                'type' => 'list_pattern',
                'reference_id' => $listId,
            ],
            [
                'workspace_id' => $workspaceId,
                'list_id' => $listId,
                'content' => $data['summary'] ?? null,
                'metadata' => $data,
            ]
        );
    }


    public function getListPatterns(int $workspaceId): Collection
    {
        return RagChunk::where('type', 'list_pattern')
            ->where('workspace_id', $workspaceId)
            ->get();
    }


    public function upsertWorkspacePatternChunk(int $workspaceId, array $data): RagChunk
    {
        return RagChunk::updateOrCreate(
            [
                'type' => 'workspace_pattern',
                'reference_id' => $workspaceId,
            ],
            [
                'workspace_id' => $workspaceId,
                'content' => $data['summary'] ?? null,
                'metadata' => $data,
            ]
        );
    }

    public function getWorkspacePattern(int $workspaceId): ?RagChunk
    {
        return RagChunk::where('type', 'workspace_pattern')
            ->where('workspace_id', $workspaceId)
            ->first();
    }


    public function getByType(string $type, array $filters = []): Collection
    {
        $query = RagChunk::where('type', $type);

        foreach ($filters as $field => $value) {
            $query->where($field, $value);
        }

        return $query->get();
    }

    public function updateChunkTags(int $chunkId, array $params): void
    {
        $chunk = RagChunk::findOrFail($chunkId);

        $metadata = $chunk->metadata ?? [];

        $tags = $params['tags'];

        $metadata['tags'] = $tags;

        $chunk->metadata = $metadata;
        $chunk->save();

        $tags = array_map(fn($tag) => ['name' => $tag], $tags);
        ChunkTag::upsert($tags, ['name']);
    }
}
