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
            'user_id' => $task->user_id,
            'workspace_id' => $task->tasklist->workspace_id,
            'tasklist_id' => $task->tasklist_id,
            'task_id' => $task->id,
            'task_description' => $task->description,
            'content' => $this->buildContent($task),
            'metadata' => $this->buildMetadata($task),
        ];
    }

    /**
     * Build the content used for embeddings / retrieval
     */
    protected function buildContent(Task $task): string
    {
        $workspace = $task->tasklist->workspace->name ?? '';
        $list = $task->tasklist->name ?? '';

        return trim(
            "Workspace: {$workspace}\n" .
                "List: {$list}\n" .
                "Task: {$task->description}"
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
