<?php

namespace App\Http\Controllers\Api\AI;

use App\Data\WorkspaceData;
use App\Http\Requests\AIWorkspaceController\GenerateAIWorkspaceRequest;
use App\Http\Controllers\Controller;
use App\Http\Requests\AIWorkspaceController\StoreWorkspaceFromAIRequest;
use App\Jobs\AI\GenerateWorkspaceJob;
use App\Models\AIJob;
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
        ]);

        GenerateWorkspaceJob::dispatch($job);

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

        $workspace = Workspace::find($job->workspace_id);

        return response()->json([
            'status' => 'done',
            'workspace' => $workspace
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

        $job->update([
            'status' => 'done',
            'workspace_id' => $workspace->id,
        ]);

        return response()->noContent();
    }
}
