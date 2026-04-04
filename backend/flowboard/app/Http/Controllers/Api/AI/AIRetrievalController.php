<?php

namespace App\Http\Controllers\Api\AI;

use App\Enums\WorkspaceType;
use App\Http\Controllers\Controller;
use App\Http\Requests\AIRetrievalController\RetrieveRequest;
use App\Services\AI\Retrieval\RetrievalOrchestratorService;

class AIRetrievalController extends Controller
{

    public function __construct(
        private RetrievalOrchestratorService $retrievalOrchestratorService
    ) {}


    public function retrieve(RetrieveRequest $request)
    {
        $user = $request->user();
        $type = WorkspaceType::from($request->validated('type'));
        $prompt = $request->input('prompt');

        return $this->retrievalOrchestratorService->orchestrate($prompt, $type, $user);
    }
}
