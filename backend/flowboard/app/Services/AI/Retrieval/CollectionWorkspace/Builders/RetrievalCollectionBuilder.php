<?php

namespace App\Services\AI\Retrieval\CollectionWorkspace\Builders;

use App\DTOs\AI\ChunkDTO;
use App\DTOs\AI\CollectionContextDTO;
use App\DTOs\AI\ExtractPatternsResponseDTO;
use App\DTOs\AI\MappedTaskListDTO;
use App\DTOs\AI\TaskListDTO;
use App\DTOs\AI\TaskListPatternsDTO;
use App\Models\AIJob;
use App\Models\RagChunk;
use App\Models\Tasklist;

class RetrievalCollectionBuilder
{

    /**
     * @param array<int, TaskListDTO> $tasklists
     * @return array<int, TaskListDTO>
     */
    public function hydrateChunks(array $tasklists): array
    {
        $chunkIds = collect($tasklists)
            ->flatMap(fn(TaskListDTO $list) => collect($list->chunks)->pluck('chunk_id'))
            ->unique()
            ->toArray();

        $chunks = RagChunk::whereIn('id', $chunkIds)
            ->get()
            ->keyBy('id');

        foreach ($tasklists as $list) {
            foreach ($list->chunks as $chunk) {
                /** @var ChunkDTO $chunk */
                $model = $chunks->get($chunk->chunk_id);

                if ($model) {
                    $chunk->task_description = $model->task_description;
                    $chunk->tags = $model->metadata['tags'] ?? [];
                }
            }
        }

        return $tasklists;
    }


    public function buildGenerationContext(ExtractPatternsResponseDTO $patternsResponse, ?AIJob $aiJob = null): CollectionContextDTO
    {
        $taskListIds = collect($patternsResponse->results)->pluck('tasklist_id');

        $listsWithData = Tasklist::with(['workspace', 'tasks'])
            ->whereIn('id', $taskListIds)
            ->get();

        $mappedLists = collect($patternsResponse->results)->map(function ($list) use ($listsWithData) {
            $dbRecord = $listsWithData->firstWhere('id', $list->tasklist_id);

            return new MappedTaskListDTO(
                tasklist_id: $list->tasklist_id,
                name: $dbRecord ? $dbRecord->name : 'Unknown',
                patterns: $list->patterns
            );
        })->all();

        $allWorkspaces = $listsWithData->pluck('workspace')->unique('id');

        if ($aiJob) {
            $aiJob->update([
                'metadata' => [
                    'source_workspace_ids' => $allWorkspaces->pluck('id')->all(),
                ]
            ]);
        }

        return new CollectionContextDTO(
            lists: $mappedLists,
            average_tasks_per_list: (int) round($listsWithData->avg(fn($l) => $l->tasks->count())),
            average_lists_per_workspace: (int) round($allWorkspaces->avg(fn($w) => $w->tasklists->count()))
        );
    }
}
