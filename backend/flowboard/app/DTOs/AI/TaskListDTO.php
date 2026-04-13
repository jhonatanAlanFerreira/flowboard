<?php

namespace App\DTOs\AI;

class TaskListDTO
{
    public function __construct(
        public int $tasklist_id,
        public float $score,
        public float $relevance,
        public int $volume,
        public float $concentration,
        public float $volume_norm,
        public array $chunks,
    ) {}
}
