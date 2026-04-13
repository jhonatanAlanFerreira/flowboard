<?php

namespace App\Services\Chunking\Builders;

use App\DTOs\AI\RagChunkDTO;
use App\Enums\RagChunkType;
use App\Models\Tasklist;

class ListChunkBuilder
{
    /**
     * Build chunk data from a Tasklist model
     */
    public function build(Tasklist $tasklist): RagChunkDTO
    {
        $tasklist->loadMissing('workspace');

        return new RagChunkDTO(
            user_id: $tasklist->user_id,
            type: RagChunkType::LIST,
            workspace_id: $tasklist->workspace_id,
            tasklist_id: $tasklist->id,
            task_id: null,
            content: $this->buildContent($tasklist),
            task_description: null,
            metadata: []
        );
    }


    /**
     * Build the content used for embeddings / retrieval
     */
    protected function buildContent(Tasklist $tasklist): string
    {
        $workspace = $tasklist->workspace->name ?? '';

        return trim(
            "{$workspace}:\n" .
                "{$tasklist->name}\n"
        );
    }
}
