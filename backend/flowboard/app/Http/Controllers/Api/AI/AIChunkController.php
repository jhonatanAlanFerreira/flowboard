<?php

namespace App\Http\Controllers\Api\AI;

use App\Http\Controllers\Controller;
use App\Http\Requests\AIChunkController\UpdateChunkTagsRequest;
use App\Services\Chunking\ChunkService;

class AIChunkController extends Controller
{
    public function __construct(
        private ChunkService $chunkService,
    ) {}


    public function updateChunkTags(UpdateChunkTagsRequest $request, $chunkId)
    {
        $this->chunkService->updateChunkTags(
            $chunkId,
            $request->validated()
        );

        return response()->noContent();
    }
}
