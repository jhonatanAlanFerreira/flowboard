<?php

namespace App\Jobs\AI;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

use App\Services\Chunking\ChunkService;

class DeleteTaskChunksFromListJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $tries = 3;
    public int $timeout = 30;

    public function __construct(public int $tasklistId) {}

    public function handle(
        ChunkService $chunkService,
    ): void {

        $chunkService->deleteTaskChunksFromList(
            $this->tasklistId
        );
    }
}
