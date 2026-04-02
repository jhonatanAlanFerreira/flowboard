<?php

namespace App\Http\Controllers\Api\AI;

use App\Http\Controllers\Controller;
use App\Http\Requests\AIRetrievalController\RetrieveRequest;
use App\Services\AI\Retrieval\Builders\RetrievalBuilder;
use App\Services\AI\Retrieval\RetrievalService;

class AIRetrievalController extends Controller
{
    public function __construct(
        private RetrievalService $retrievalService,
        private RetrievalBuilder $retrievalBuilder
    ) {}

    public function retrieve(RetrieveRequest $request)
    {
        $user = $request->user();

        $listsRes = $this->retrievalService->retrieveLists($request->input('prompt'), $user->id);

        return $this->retrievalBuilder->hydrateChunks($listsRes);
    }
}
