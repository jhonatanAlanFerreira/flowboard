<?php

namespace App\Services\AI\Agents;

use App\Enums\WorkspaceType;
use App\Models\AIJob;
use App\Services\AI\Retrieval\RetrievalOrchestratorService;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class WorkspaceGeneratorAgent
{
    public function __construct(private RetrievalOrchestratorService $retrievalOrchestratorService) {}

    /**
     * Generate collection workspace from prompt using Python API
     */
    public function generateCollectionWorkspace(AIJob $job): array
    {
        $data = $this->retrievalOrchestratorService->orchestrate(
            $job->prompt,
            WorkspaceType::COLLECTION,
            $job->user,
            $job
        );

        $payload = $this->buildCollectionWorkspacePayload($data, $job);

        try {
            $response = Http::ai()
                ->timeout(10)
                ->post('/generate-workspace/collection', $payload);

            if ($response->successful()) {
                return $response->json();
            }

            Log::warning('WorkspaceGeneratorAgent failed', [
                'status' => $response->status(),
                'body' => $response->body(),
            ]);
        } catch (\Throwable $e) {
            Log::warning('WorkspaceGeneratorAgent exception', [
                'message' => $e->getMessage(),
            ]);
        }


        Log::error('WorkspaceGeneratorAgent completely unavailable after retries');

        throw new \RuntimeException('AI API is not responding');
    }

    private function buildCollectionWorkspacePayload($data, AIJob $job)
    {

        $lists = collect($data['lists'])->map(fn($list) => [
            'name'  => $list['name'],
            'tasks' => collect($list['patterns'])->pluck('task')->all(),
        ])->all();

        return [
            'job_id' => $job->id,
            'lists' => $lists,
            'prompt' => $job->prompt,
            'average_tasks_per_list'      => $data['average_tasks_per_list'],
            'average_lists_per_workspace' => $data['average_lists_per_workspace'],
        ];
    }


    /**
     * Generate workflow workspace from prompt using Python API
     */
    public function generateWorkflowWorkspace(AIJob $job): array
    {
        $data = $this->retrievalOrchestratorService->orchestrate(
            $job->prompt,
            WorkspaceType::WORKFLOW,
            $job->user,
            $job
        );

        $payload = $this->buildWorkflowWorkspacePayload($data, $job);

        try {
            $response = Http::ai()
                ->timeout(10)
                ->post('/generate-workspace/workflow', $payload);

            if ($response->successful()) {
                return $response->json();
            }

            Log::warning('WorkspaceGeneratorAgent failed', [
                'status' => $response->status(),
                'body' => $response->body(),
            ]);
        } catch (\Throwable $e) {
            Log::warning('WorkspaceGeneratorAgent exception', [
                'message' => $e->getMessage(),
            ]);
        }


        Log::error('WorkspaceGeneratorAgent completely unavailable after retries');

        throw new \RuntimeException('AI API is not responding');
    }


    private function buildWorkflowWorkspacePayload($data, AIJob $job)
    {

        return [
            'job_id' => $job->id,
            'lists' => $data['lists'],
            'prompt' => $job->prompt,
            'average_lists_per_workspace' => $data['average_lists_per_workspace'],
        ];
    }
}
