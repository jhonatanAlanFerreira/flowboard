<?php

namespace App\DTOs\AI;

class ChunkDTO
{
    public function __construct(
        public int $chunk_id,
        public float $score,
    ) {}
}
