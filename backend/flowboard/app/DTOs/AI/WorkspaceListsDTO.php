<?php

namespace App\DTOs\AI;

class WorkspaceListsDTO
{
    /**
     * @param array<int, string> $lists
     */
    public function __construct(
        public string $workspace_id,
        public array $lists,
    ) {}
}
