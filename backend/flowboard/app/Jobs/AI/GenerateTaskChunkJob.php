<?php

namespace App\Jobs\AI;

use App\Models\Task;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

use App\Services\Chunking\ChunkService;
use App\Services\Chunking\Builders\TaskChunkBuilder;

class GenerateTaskChunkJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $tries = 3;
    public int $timeout = 30;

    public function __construct(public Task $task) {}

    public function handle(
        ChunkService $chunkService,
        TaskChunkBuilder $taskChunkBuilder
    ): void {

        $chunkData = $taskChunkBuilder->build($this->task);

        $chunk = $chunkService->upsertTaskChunk(
            taskId: $this->task->id,
            data: $chunkData
        );

        // GenerateTaskTagsJob::dispatch($chunk->id);
        // GenerateEmbeddingJob::dispatch($chunk->id);

        // update has_embeddings and tags
    }
}
