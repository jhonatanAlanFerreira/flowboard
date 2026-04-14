<?php

namespace App\Services\Chunking\Builders;

use App\DTOs\AI\RagChunkDTO;
use App\Enums\RagChunkType;
use App\Models\Workspace;

class WorkspaceChunkBuilder
{
    /**
     * Build chunk data from a Workspace model
     */


    public function build(Workspace $workspace): RagChunkDTO
    {
        return new RagChunkDTO(
            user_id: $workspace->user_id,
            type: RagChunkType::WORKSPACE,
            workspace_id: $workspace->id,
            tasklist_id: null,
            task_id: null,
            content: $workspace->name,
            task_description: null,
            metadata: []
        );
    }
}
