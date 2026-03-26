<?php

namespace App\Services\Chunking\Builders;

use App\Models\Task;

class TaskChunkBuilder
{
    /**
     * Build chunk data from a Task model
     */
    public function build(Task $task): array
    {
        $task->loadMissing('tasklist.workspace');

        return [
            'type' => 'task',

            'user_id' => $task->user_id,
            'workspace_id' => $task->tasklist->workspace_id,
            'tasklist_id' => $task->tasklist_id,
            'task_id' => $task->id,

            'content' => $this->buildContent($task),

            // Structured metadata (used later for patterns)
            'metadata' => $this->buildMetadata($task),
        ];
    }

    /**
     * Build the content used for embeddings / retrieval
     */
    protected function buildContent(Task $task): string
    {
        // For now: just description (cleaned)
        return trim($task->description);
    }

    /**
     * Build structured metadata
     */
    protected function buildMetadata(Task $task): array
    {
        return [
            'created_at' => $task->created_at?->toISOString(),
            'updated_at' => $task->updated_at?->toISOString(),

            // Future-ready fields
            'tags' => [], // will be filled by AI later
        ];
    }
}
