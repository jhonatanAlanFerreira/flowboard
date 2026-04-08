<?php

namespace App\Services\AI\Retrieval;

use App\Enums\WorkspaceType;
use App\Models\AIJob;
use App\Models\User;
use App\Services\AI\Retrieval\CollectionWorkspace\Builders\RetrievalCollectionBuilder;
use App\Services\AI\Retrieval\CollectionWorkspace\RetrievalCollectionService;
use App\Services\AI\Retrieval\WorkflowWorkspace\Builders\RetrievalWorkflowBuilder;
use App\Services\AI\Retrieval\WorkflowWorkspace\RetrievalWorkflowService;

class RetrievalOrchestratorService
{

    public function __construct(
        private RetrievalCollectionService $retrievalCollectionService,
        private RetrievalWorkflowService $retrievalWorkflowService,
        private RetrievalCollectionBuilder $retrievalCollectionBuilder,
        private RetrievalWorkflowBuilder $retrievalWorkflowBuilder,
    ) {}


    public function orchestrate(string $prompt, WorkspaceType $type, User $user, ?AIJob $aiJob = null)
    {
        if ($type === WorkspaceType::COLLECTION) {
            $listsRes = $this->retrievalCollectionService->retrieveLists($prompt, $user->id);
            $listsRes = $this->retrievalCollectionBuilder->hydrateChunks($listsRes);
            $patterns = $this->retrievalCollectionService->extractPatternsFromCollectionWorkflow($listsRes);
            return $this->retrievalCollectionBuilder->buildGenerationContext($patterns['results'], $aiJob);
        }

        if ($type === WorkspaceType::WORKFLOW) {
            $res = $this->retrievalWorkflowService->retrieveLists($prompt, $user->id);
            $lists = $this->retrievalWorkflowBuilder->getListsFromWorkspaces($res);
            return $this->retrievalWorkflowBuilder->buildGenerationContext($lists);
        }
    }
}
