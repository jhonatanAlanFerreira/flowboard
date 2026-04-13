<?php

namespace App\DTOs\AI;

class CollectionContextDTO
{
    /**
     * @param MappedTaskListDTO[] $lists
     */
    public function __construct(
        public array $lists,
        public int $average_tasks_per_list,
        public int $average_lists_per_workspace,
    ) {}
}
