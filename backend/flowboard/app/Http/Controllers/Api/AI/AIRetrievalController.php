<?php

namespace App\Http\Controllers\Api\AI;

use App\Enums\WorkspaceType;
use App\Http\Controllers\Controller;
use App\Http\Requests\AIRetrievalController\RetrieveRequest;
use App\Services\AI\Retrieval\CollectionWorkspace\Builders\RetrievalCollectionBuilder;
use App\Services\AI\Retrieval\CollectionWorkspace\RetrievalCollectionService;
use App\Services\AI\Retrieval\WorkflowWorkspace\RetrievalWorkflowService;

class AIRetrievalController extends Controller
{
    public function __construct(
        private RetrievalCollectionService $retrievalCollectionService,
        private RetrievalWorkflowService $retrievalWorkflowService,
        private RetrievalCollectionBuilder $retrievalBuilder
    ) {}

    public function retrieve(RetrieveRequest $request)
    {
        $user = $request->user();
        $type = WorkspaceType::from($request->validated('type'));

        if ($type === WorkspaceType::COLLECTION) {
            $listsRes = $this->retrievalCollectionService->retrieveLists($request->input('prompt'), $user->id);
            $listsRes = $this->retrievalBuilder->hydrateChunks($listsRes);
            return $this->retrievalCollectionService->extractPatternsFromCollectionWorkflow($listsRes);
        }

        if ($type === WorkspaceType::WORKFLOW) {
            $res = $this->retrievalWorkflowService->retrieveLists($request->input('prompt'), $user->id);
            return $res;
        }
    }
}
