<?php

namespace App\Http\Controllers\Api\AI;

use App\Enums\WorkspaceType;
use App\Http\Controllers\Controller;
use App\Http\Requests\AIRetrievalController\RetrievalRequest;
use App\Services\AI\Retrieval\RetrievalOrchestratorService;

class AIRetrievalController extends Controller
{

    public function __construct(
        private RetrievalOrchestratorService $retrievalOrchestratorService
    ) {}


    public function retrieve(RetrievalRequest $request)
    {
        $user = $request->user();
        $type = WorkspaceType::from($request->validated('type'));
        $prompt = $request->input('prompt');

        $res = $this->retrievalOrchestratorService->orchestrate($prompt, $type, $user);

        return response()->json($res);
    }
}
