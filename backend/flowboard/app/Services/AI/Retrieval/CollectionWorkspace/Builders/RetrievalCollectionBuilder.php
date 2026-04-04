<?php

namespace App\Services\AI\Retrieval\CollectionWorkspace\Builders;

use App\Models\RagChunk;
use App\Models\Tasklist;
use App\Models\Workspace;
use App\Services\AI\Retrieval\DTO\TaskListDTO;

class RetrievalCollectionBuilder
{
    /**
     * @param TaskListDTO[]
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


    /**
     * @param TaskListDTO[] $taskLists
     */
    public function buildGenerationContext(array $taskLists): array
    {
        $taskListIds = collect($taskLists)->pluck('tasklist_id')->unique();

        $workspaceIds = Tasklist::whereIn('id', $taskListIds)
            ->pluck('workspace_id')
            ->unique();

        $workspaces = Workspace::with(['tasklists.tasks'])
            ->whereIn('id', $workspaceIds)
            ->get();

        $allTasklists = $workspaces->flatMap->tasklists;

        return [
            'lists' => $taskLists,
            'average_tasks_per_list' => round($allTasklists->avg(fn($list) => $list->tasks->count())),
            'average_lists_per_workspace' => round($workspaces->avg(fn($workspace) => $workspace->tasklists->count()))
        ];
    }
}
