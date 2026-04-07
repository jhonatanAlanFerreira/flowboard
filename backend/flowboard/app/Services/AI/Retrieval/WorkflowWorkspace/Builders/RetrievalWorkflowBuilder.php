<?php

namespace App\Services\AI\Retrieval\WorkflowWorkspace\Builders;

use App\Models\AIJob;
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

    public function buildGenerationContext(array $workflowLists, ?AIJob $aiJob = null): array
    {
        $workspaceIds = array_column($workflowLists, 'workspace_id');

        $allListNames = [];
        foreach ($workflowLists as $item) {
            $allListNames = array_merge($allListNames, $item['lists']);
        }

        $totalWorkspaces = count($workflowLists);
        $totalLists = count($allListNames);
        $average = $totalWorkspaces > 0 ? $totalLists / $totalWorkspaces : 0;

        if ($aiJob) {
            $aiJob->update([
                'metadata' => [
                    'source_workspace_ids' => $workspaceIds
                ]
            ]);
        }

        return [
            'lists' => array_values(array_unique($allListNames)),
            'average_lists_per_workspace' => round($average),
        ];
    }
}
