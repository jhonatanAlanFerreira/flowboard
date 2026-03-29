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


    public function deleteTaskChunk(int $taskId): void
    {
        RagChunk::where('reference_id', $taskId)
            ->delete();
    }


    public function getTaskChunksByList(int $listId): Collection
    {
        return RagChunk::where('list_id', $listId)
            ->get();
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
