<?php

namespace App\Services\AI\Retrieval\CollectionWorkspace\Builders;

use App\Models\RagChunk;
use App\Models\Tasklist;
use App\Models\Workspace;
use App\Services\AI\Retrieval\CollectionWorkspace\DTO\TaskListDTO;

class RetrievalCollectionBuilder
{
    /**
     * @param TaskListDTO[]
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


    /**
     * @param TaskListDTO[] $taskLists
     */
    public function buildGenerationContext(array $taskLists): array
    {
        $taskListIds = collect($taskLists)->pluck('tasklist_id');

        // Fetch tasklists with workspace and tasks in fewer queries
        $listsWithData = Tasklist::with(['workspace', 'tasks'])
            ->whereIn('id', $taskListIds)
            ->get();

        // Map names to input array
        $mappedLists = collect($taskLists)->map(function ($list) use ($listsWithData) {
            $list['name'] = $listsWithData->firstWhere('id', $list['tasklist_id'])->name;
            return $list;
        })->all();

        $allWorkspaces = $listsWithData->pluck('workspace')->unique('id');

        return [
            'lists' => $mappedLists,
            'average_tasks_per_list' => round($listsWithData->avg(fn($l) => $l->tasks->count())),
            'average_lists_per_workspace' => round($allWorkspaces->avg(fn($w) => $w->tasklists->count()))
        ];
    }
}
