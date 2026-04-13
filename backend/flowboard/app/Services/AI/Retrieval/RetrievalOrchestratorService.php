<?php

namespace App\Services\AI\Retrieval;

use App\DTOs\AI\CollectionContextDTO;
use App\DTOs\AI\ExtractPatternsResponseDTO;
use App\DTOs\AI\TaskListDTO;
use App\DTOs\AI\WorkflowContextDTO;
use App\DTOs\AI\WorkspaceDTO;
use App\DTOs\AI\WorkspaceListsDTO;
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


    public function orchestrate(string $prompt, WorkspaceType $type, User $user, ?AIJob $aiJob = null): CollectionContextDTO|WorkflowContextDTO|null
    {
        if ($type === WorkspaceType::COLLECTION) {

            /** @var TaskListDTO[] $workspaceLists */
            $workspaceLists = $this->retrievalCollectionService->retrieveLists($prompt, $user->id);
            $workspaceLists = $this->retrievalCollectionBuilder->hydrateChunks($workspaceLists);

            /** @var ExtractPatternsResponseDTO $patterns */
            $patterns = $this->retrievalCollectionService->extractPatternsFromCollectionWorkspace($workspaceLists);

            return $this->retrievalCollectionBuilder->buildGenerationContext($patterns, $aiJob);
        }

        if ($type === WorkspaceType::WORKFLOW) {

            /** @var WorkspaceDTO[] $workspacesScores */
            $workspacesScores = $this->retrievalWorkflowService->retrieveWorkspaces($prompt, $user->id);

            /** @var WorkspaceListsDTO[] $workspaceLists */
            $workspaceLists = $this->retrievalWorkflowBuilder->getListsFromWorkspaces($workspacesScores);

            return $this->retrievalWorkflowBuilder->buildGenerationContext($workspaceLists);
        }

        return null;
    }
}
