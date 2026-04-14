<?php

namespace App\DTOs\AI;

class WorkspaceDTO
{
    public function __construct(
        public string $workspace_id,
        public float $score,
        public float $max_score,
        public int $match_count,
        public string $chunk_id,
        public float $final_score,
    ) {}
}
