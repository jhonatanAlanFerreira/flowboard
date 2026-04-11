<?php

namespace App\Http\Controllers\Api\AI;

use App\Http\Controllers\Controller;
use App\Http\Requests\AIDataQuestionController\DataQuestionCompleteRequest;
use App\Http\Requests\AIDataQuestionController\HydrateDataQuestionRetrievalRequest;
use App\Models\AIJob;
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

    public function dataQuestionComplete(DataQuestionCompleteRequest $request, $jobId)
    {
        $aiJob = AIJob::find($jobId);

        $aiJob->metadata = [
            'source_chunk_ids' => $request->input('citations'),
            'answer' => $request->input('markdown_answer'),
        ];

        $aiJob->status = 'done';
        $aiJob->save();

        return response()->json([
            'status' => 'ok',
            'message' => "Job {$jobId} completed successfully."
        ]);
    }
}
