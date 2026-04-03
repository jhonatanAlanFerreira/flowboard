<?php 

namespace App\Services\AI\Retrieval\CollectionWorkspace\DTO;

class ChunkDTO
{
    public function __construct(
        public int $chunk_id,
        public float $score,
        public ?string $task_description = null,
        public array $tags = [],
    ) {}
}