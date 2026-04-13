<?php

namespace App\DTOs\AI;

use App\Enums\RagChunkType;

class RagChunkDTO
{
    public function __construct(
        public int $user_id,
        public RagChunkType $type,
        public int $workspace_id,
        public ?int $tasklist_id,
        public ?int $task_id,
        public string $content,
        public ?string $task_description = null,
        public array $metadata = [],
    ) {}
}
