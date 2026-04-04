<?php

namespace App\Services\AI\Retrieval\WorkflowWorkspace\Builders;

use App\Models\Workspace;
use App\Services\AI\Retrieval\WorkflowWorkspace\DTO\WorkspaceDTO;

class RetrievalWorkflowBuilder
{
    /**
     * @param WorkspaceDTO[]
     */
    public function getListsFromWorkspaces(array $data): array
    {
        return array_map(function (WorkspaceDTO $item) {
            return  [
                'workspace_id' => $item->workspace_id,
                'lists' => Workspace::find($item->workspace_id)->tasklists()->pluck('name')->toArray()
            ];
        }, $data);
    }
}
