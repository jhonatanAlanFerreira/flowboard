<?php

namespace App\Services\AI;

use App\Models\RagChunk;
use App\Models\Workspace;

class DataQuestionService
{
    public function __construct() {}

    public function hydrateChunk($chunks)
    {
        foreach ($chunks as &$chunk) {
            $task = RagChunk::find($chunk['chunk_id'])->task;
            $workspace = Workspace::find($chunk['workspace_id']);

            $chunk['done'] = $task->done;
            $chunk['created_at'] = $task->created_at;
            $chunk['workspace_name'] = $workspace->name;
        }

        return $chunks;
    }
}
