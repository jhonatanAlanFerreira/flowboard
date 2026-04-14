<?php

namespace App\DTOs\AI;

class PatternDTO
{
    public function __construct(
        public string $tag,
        public float $score,
        public string $task,
    ) {}
}
