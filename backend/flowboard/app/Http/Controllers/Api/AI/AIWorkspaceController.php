<?php

namespace App\Http\Controllers\Api\AI;

use App\Data\WorkspaceData;
use App\Enums\AIJobsType;
use App\Http\Requests\AIWorkspaceController\GenerateAIWorkspaceRequest;
use App\Http\Controllers\Controller;
use App\Http\Requests\AIWorkspaceController\DataQuestionRequest;
use App\Http\Requests\AIWorkspaceController\StoreWorkspaceFromAIRequest;
use App\Jobs\AI\GenerateWorkspaceJob;
use App\Jobs\AI\ProcessUserQuestionJob;
use App\Models\AIJob;
use App\Models\RagChunk;
use App\Models\Task;
use App\Models\Workspace;
use App\Services\Workspace\WorkspaceService;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class AIWorkspaceController extends Controller
{
    public function __construct(
        private WorkspaceService $workspaceService
    ) {}


    public function generate(
        GenerateAIWorkspaceRequest $request,
    ): JsonResponse {
        $job = AIJob::create([
            'user_id' => $request->user()->id,
            'status' => 'pending',
            'prompt' => $request->prompt,
            'type' => $request->type
        ]);

        GenerateWorkspaceJob::dispatch($job);

        return response()->json([
            'status' => 'accepted'
        ], 202);
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

        if ($job->type == AIJobsType::USER_QUESTION->value) {
            $answer = $job->metadata['answer'];
            $chunkIDs = $job->metadata['source_chunk_ids'];

            $chunks = RagChunk::whereIn('id', $chunkIDs)->get();
            $taskIDs = $chunks->pluck('task_id')->filter()->unique()->toArray();

            $tasks = Task::with('workspace')
                ->whereIn('id', $taskIDs)
                ->get()
                ->values();

            return response()->json([
                'status' => 'done',
                'answer' => $answer,
                'source_tasks' => $tasks,
            ]);
        }

        $workspace = Workspace::find($job->workspace_id);

        $sourceWorkspaceNames = Workspace::whereIn('id', $job->metadata['source_workspace_ids'] ?? [])->pluck('name')->toArray();

        return response()->json([
            'status' => 'done',
            'workspace' => $workspace,
            'source_workspace_names' => $sourceWorkspaceNames,
        ]);
    }

    public function checkAiEndpoint(): bool
    {
        try {
            $response = Http::ai()
                ->timeout(2)
                ->connectTimeout(1)
                ->get('/health');

            if ($response->successful()) {
                return true;
            }

            Log::warning('AI health check failed (non-200 response)', [
                'status' => $response->status(),
                'body' => $response->body(),
            ]);

            return false;
        } catch (\Throwable $e) {
            Log::warning('AI health check failed (exception)', [
                'error' => $e->getMessage(),
            ]);

            return false;
        }
    }

    public function storeFromAI(StoreWorkspaceFromAIRequest $request)
    {
        $params = new StoreWorkspaceFromAIRequest($request->validated());
        $workspaceData = new WorkspaceData($request->validated());

        $job = AIJob::find($params->job_id);
        $userId = $job->user->id;

        $workspace = $this->workspaceService->persistWorkspace($workspaceData, $userId);

        $sourceWorkspaceIds = $request->source_workspace_ids;

        $jobParamsToUpdate = [
            'status' => 'done',
            'workspace_id' => $workspace->id,
        ];

        if ($sourceWorkspaceIds) {
            $jobParamsToUpdate['metadata'] = [
                'source_workspace_ids' => $sourceWorkspaceIds,
            ];
        }

        $job->update($jobParamsToUpdate);

        return response()->noContent();
    }
}
