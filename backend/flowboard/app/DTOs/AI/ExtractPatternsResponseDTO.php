<?php

namespace App\DTOs\AI;

class ExtractPatternsResponseDTO
{
    /**
     * @param TaskListPatternsDTO[] $results
     */
    public function __construct(
        public array $results
    ) {}
}
