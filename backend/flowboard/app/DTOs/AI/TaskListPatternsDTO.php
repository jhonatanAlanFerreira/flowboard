<?php

namespace App\DTOs\AI;

class TaskListPatternsDTO
{
    /**
     * @param PatternDTO[] $patterns
     */
    public function __construct(
        public int $tasklist_id,
        public array $patterns,
    ) {}
}
