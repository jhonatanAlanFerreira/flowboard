<?php

namespace App\DTOs\AI;

class MappedTaskListDTO
{
    /**
     * @param PatternDTO[] $patterns
     */
    public function __construct(
        public int $tasklist_id,
        public string $name,
        public array $patterns,
    ) {}
}
