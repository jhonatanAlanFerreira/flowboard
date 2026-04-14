<?php

namespace App\DTOs\AI;

use App\DTOs\AI\WorkspaceListsDTO;

class WorkflowContextDTO
{
    /**
     * @param WorkspaceListsDTO[] $workflowLists
     */
    public function __construct(
        public array $workflowLists,
        public int $average_lists_per_workspace,
    ) {}
}
