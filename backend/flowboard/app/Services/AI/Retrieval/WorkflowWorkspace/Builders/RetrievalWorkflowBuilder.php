<?php

namespace App\Services\AI\Retrieval\WorkflowWorkspace\Builders;

use App\DTOs\AI\WorkflowContextDTO;
use App\DTOs\AI\WorkspaceDTO;
use App\DTOs\AI\WorkspaceListsDTO;
use App\Models\Workspace;

class RetrievalWorkflowBuilder
{
    /**
     * @param array<int, WorkspaceDTO> $workspacesScores
     * @return array<int, WorkspaceListsDTO>
     */
    public function getListsFromWorkspaces(array $workspacesScores): array
    {
        if (empty($workspacesScores)) {
            return [];
        }

        $workspaceIds = array_map(fn(WorkspaceDTO $item) => $item->workspace_id, $workspacesScores);

        $workspaces = Workspace::whereIn('id', $workspaceIds)
            ->with('tasklists')
            ->get()
            ->keyBy('id');

        return array_map(function (WorkspaceDTO $item) use ($workspaces) {
            $workspace = $workspaces->get($item->workspace_id);

            $lists = $workspace
                ? $workspace->tasklists->pluck('name')->toArray()
                : [];

            return new WorkspaceListsDTO(
                workspace_id: $item->workspace_id,
                lists: $lists
            );
        }, $workspacesScores);
    }


    /**
     * @param array<int, WorkspaceListsDTO> $workflowLists
     */
    public function buildGenerationContext(array $workflowLists): WorkflowContextDTO
    {
        $allListNames = [];

        foreach ($workflowLists as $item) {
            $allListNames = array_merge($allListNames, $item->lists);
        }

        $totalWorkspaces = count($workflowLists);
        $totalLists = count($allListNames);
        $average = $totalWorkspaces > 0 ? $totalLists / $totalWorkspaces : 0;

        return new WorkflowContextDTO(
            workflowLists: $workflowLists,
            average_lists_per_workspace: (int) round($average)
        );
    }
}
