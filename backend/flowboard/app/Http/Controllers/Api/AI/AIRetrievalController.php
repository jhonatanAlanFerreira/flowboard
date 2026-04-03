<?php

namespace App\Http\Controllers\Api\AI;

use App\Enums\WorkspaceType;
use App\Http\Controllers\Controller;
use App\Http\Requests\AIRetrievalController\RetrieveRequest;
use App\Services\AI\Retrieval\CollectionWorkspace\Builders\RetrievalCollectionBuilder;
use App\Services\AI\Retrieval\CollectionWorkspace\RetrievalCollectionService;

class AIRetrievalController extends Controller
{
    public function __construct(
        private RetrievalCollectionService $retrievalService,
        private RetrievalCollectionBuilder $retrievalBuilder
    ) {}

    public function retrieve(RetrieveRequest $request)
    {
        $user = $request->user();
        $type = WorkspaceType::from($request->validated('type'));

        if ($type === WorkspaceType::COLLECTION) {
            $listsRes = $this->retrievalService->retrieveLists($request->input('prompt'), $user->id);
            $listsRes = $this->retrievalBuilder->hydrateChunks($listsRes);
            return $this->retrievalService->extractPatternsFromCollectionWorkflow($listsRes);
        }
    }
}
