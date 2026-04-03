<?php

namespace App\Services\Chunking\Builders;

use App\Models\Tasklist;

class ListChunkBuilder
{
    /**
     * Build chunk data from a Tasklist model
     */
    public function build(Tasklist $tasklist): array
    {
        $tasklist->loadMissing('workspace');

        return [
            'user_id' => $tasklist->user_id,
            'type' => 'list',
            'workspace_id' => $tasklist->workspace_id,
            'tasklist_id' => $tasklist->id,
            'content' => $this->buildContent($tasklist),
        ];
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
