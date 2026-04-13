<?php

namespace App\Jobs\AI\Workspace;

use App\DTOs\AI\RagChunkDTO;
use App\Models\RagChunk;
use App\Models\Workspace;
use App\Services\Chunking\ChunkService;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use App\Services\Chunking\Builders\WorkspaceChunkBuilder;

class GenerateWorkspaceChunkJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $tries = 3;
    public int $timeout = 30;

    public function __construct(public Workspace $workspace) {}

    public function handle(
        ChunkService $chunkService,
        WorkspaceChunkBuilder $workspaceChunkBuilder,
    ): void {

        /** @var RagChunkDTO $chunkData */
        $chunkData = $workspaceChunkBuilder->build($this->workspace);

        /** @var RagChunk $chunk */
        $chunk = $chunkService->upsertChunk($chunkData);

        $chunkService->createWorkspaceChunks($chunk);
    }
}
