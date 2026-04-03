<?php

namespace App\Services\AI\Retrieval\CollectionWorkspace\Builders;

use App\Models\RagChunk;
use App\Services\AI\Retrieval\DTO\TaskListDTO;

class RetrievalCollectionBuilder
{
    /**
     * @param TaskListDTO[] $tasklists
     * @return TaskListDTO[]
     */
    public function hydrateChunks(array $tasklists): array
    {
        $chunkIds = collect($tasklists)
            ->flatMap(fn($list) => collect($list->chunks)->pluck('chunk_id'))
            ->unique();

        $chunks = RagChunk::whereIn('id', $chunkIds)
            ->get()
            ->keyBy('id');

        foreach ($tasklists as $list) {
            foreach ($list->chunks as $chunk) {
                $model = $chunks->get($chunk->chunk_id);

                if ($model) {
                    $chunk->task_description = $model->task_description;
                    $chunk->tags = $model->metadata['tags'] ?? [];
                }
            }
        }

        return $tasklists;
    }
}
