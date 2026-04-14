<?php

namespace App\DTOs\AI;

class ChunkDTO
{
    /**
     * @param array<int, string> $tags
     */
    public function __construct(
        public int $chunk_id,
        public float $score,
        public ?string $task_description = null,
        public array $tags = [],
    ) {}
}
