<?php

namespace App\Services\Chunking\Builders;

use App\DTOs\AI\RagChunkDTO;
use App\Enums\RagChunkType;
use App\Models\Task;

class TaskChunkBuilder
{
    /**
     * Build chunk data from a Task model
     */
    public function build(Task $task): RagChunkDTO
    {
        $task->loadMissing('tasklist.workspace');

        return new RagChunkDTO(
            user_id: $task->user_id,
            type: RagChunkType::TASK,
            workspace_id: $task->tasklist->workspace_id,
            tasklist_id: $task->tasklist_id,
            task_id: $task->id,
            task_description: $task->description,
            content: $this->buildContent($task),
            metadata: $this->buildMetadata($task),
        );
    }

    /**
     * Build the content used for embeddings / retrieval
     */
    protected function buildContent(Task $task): string
    {
        $list = $task->tasklist->name ?? '';

        return trim(
            "{$list}:\n" .
                "{$task->description}"
        );
    }

    /**
     * Build structured metadata
     */
    protected function buildMetadata(Task $task): array
    {
        return [
            'created_at' => $task->created_at?->toISOString(),
            'updated_at' => $task->updated_at?->toISOString(),
            'tags' => [], // will be filled by AI later
        ];
    }
}
