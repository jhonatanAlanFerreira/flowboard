<?php

namespace App\Http\Controllers\Api;

use App\Http\Requests\AIWorkspaceController\GenerateAIWorkspaceRequest;
use App\Http\Controllers\Controller;
use App\Jobs\ProcessAIWorkspace;
use App\Models\AIJob;
use App\Models\Workspace;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class AIWorkspaceController extends Controller
{
    public function generate(
        GenerateAIWorkspaceRequest $request,
    ): JsonResponse {
        $job = AIJob::create([
            'user_id' => $request->user()->id,
            'status' => 'pending',
            'prompt' => $request->prompt,
        ]);

        ProcessAIWorkspace::dispatch($job);

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
            $response = Http::timeout(2)
                ->connectTimeout(1)
                ->get(config('services.ai.endpoint') . '/health');

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
}
