<?php

namespace App\Http\Controllers\Api;

use App\Http\Requests\AIWorkspaceController\GenerateAIWorkspaceRequest;
use App\Http\Controllers\Controller;
use App\Jobs\ProcessAIWorkspace;
use App\Models\AIJob;
use App\Models\Workspace;
use Illuminate\Http\JsonResponse;

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

        $workspace = Workspace::with('lists.tasks')
            ->find($job->workspace_id);

        return response()->json([
            'status' => 'done',
            'workspace' => $workspace
        ]);
    }
}
