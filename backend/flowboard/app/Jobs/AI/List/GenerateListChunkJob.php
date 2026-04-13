<?php

namespace App\Jobs\AI\List;

use App\DTOs\AI\RagChunkDTO;
use App\Models\RagChunk;
use App\Models\Tasklist;
use App\Services\Chunking\ChunkService;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use App\Services\Chunking\Builders\ListChunkBuilder;

class GenerateListChunkJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $tries = 3;
    public int $timeout = 30;

    public function __construct(public Tasklist $tasklist) {}

    public function handle(
        ChunkService $chunkService,
        ListChunkBuilder $listChunkBuilder,
    ): void {

        /** @var RagChunkDTO $chunkData */
        $chunkData = $listChunkBuilder->build($this->tasklist);

        /** @var RagChunk $chunk */
        $chunk = $chunkService->upsertChunk($chunkData);

        $chunkService->createListChunks($chunk);
    }
}
