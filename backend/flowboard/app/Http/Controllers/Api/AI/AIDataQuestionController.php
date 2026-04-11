<?php

namespace App\Http\Controllers\Api\AI;

use App\Http\Controllers\Controller;
use App\Http\Requests\AIDataQuestionController\HydrateDataQuestionRetrievalRequest;
use App\Services\AI\Agents\GenerateAnswerAgent;
use App\Services\AI\DataQuestionService;

class AIDataQuestionController extends Controller
{
    public function __construct(
        private DataQuestionService $dataQuestionService,
        private GenerateAnswerAgent $generateAnswerAgent
    ) {}

    public function hydrateDataQuestionRetrieval(HydrateDataQuestionRetrievalRequest $request, int $jobId)
    {
        $chunks = $this->dataQuestionService->hydrateChunk($request->validated());

        $this->generateAnswerAgent->generateAnswer($chunks, $jobId);

        return response()->json([
            'status' => 'accepted'
        ], 202);
    }
}
