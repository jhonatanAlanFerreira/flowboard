<?php

namespace App\Services\Chunking\Builders;

use App\Models\Workspace;

class WorkspaceChunkBuilder
{
    /**
     * Build chunk data from a Workspace model
     */
    public function build(Workspace $workspace): array
    {

        return [
            'user_id' => $workspace->user_id,
            'type' => 'workspace',
            'workspace_id' => $workspace->id,
            'content' => $workspace->name,
        ];
    }
}
