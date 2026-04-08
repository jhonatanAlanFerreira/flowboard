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

    public function buildGenerationContext(array $workflowLists): array
    {
        $allListNames = [];
        foreach ($workflowLists as $item) {
            $allListNames = array_merge($allListNames, $item['lists']);
        }

        $totalWorkspaces = count($workflowLists);
        $totalLists = count($allListNames);
        $average = $totalWorkspaces > 0 ? $totalLists / $totalWorkspaces : 0;

        return [
            'workflowLists' => $workflowLists,
            'average_lists_per_workspace' => round($average),
        ];
    }
}
