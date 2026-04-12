<?php

namespace App\Http\Controllers\Api\AI;

use App\Enums\AIJobsType;
use App\Http\Controllers\Controller;
use App\Http\Requests\AIDataQuestionController\DataQuestionCompleteRequest;
use App\Http\Requests\AIDataQuestionController\DataQuestionRequest;
use App\Http\Requests\AIDataQuestionController\HydrateDataQuestionRetrievalRequest;
use App\Jobs\AI\ProcessUserQuestionJob;
use App\Models\AIJob;
use App\Models\RagChunk;
use App\Models\Task;
use App\Services\AI\Agents\GenerateAnswerAgent;
use App\Services\AI\DataQuestionService;
use Illuminate\Http\JsonResponse;

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

    public function dataQuestion(DataQuestionRequest $request)
    {
        $job = AIJob::create([
            'user_id' => $request->user()->id,
            'status' => 'pending',
            'prompt' => $request->prompt,
            'type' => AIJobsType::USER_QUESTION->value
        ]);

        ProcessUserQuestionJob::dispatch($job);

        return response()->json([
            'status' => 'accepted'
        ], 202);
    }

    public function latest(): JsonResponse
    {
        $job = AIJob::where('user_id', auth()->id())
            ->isDataQuestion()
            ->latest()
            ->first();

        if (!$job) {
            return response()->json(['status' => 'empty']);
        }

        if ($job->isPending()) {
            return response()->json(['status' => 'pending']);
        }

        if ($job->isFailed()) {
            return response()->json(['status' => 'failed']);
        }

        $answer = $job->metadata['answer'];
        $chunkIDs = $job->metadata['source_chunk_ids'];

        $chunks = RagChunk::whereIn('id', $chunkIDs)->get();
        $taskIDs = $chunks->pluck('task_id')->filter()->unique()->toArray();

        $tasks = Task::with('tasklist.workspace')
            ->whereIn('id', $taskIDs)
            ->get();

        return response()->json([
            'status' => 'done',
            'answer' => $answer,
            'source_tasks' => $tasks,
        ]);
    }
}
