<?php

namespace App\Jobs\AI;

use App\Enums\AIJobsType;
use App\Models\AIJob;
use App\Services\AI\Agents\WorkspaceGeneratorAgent;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;

class GenerateWorkspaceJob implements ShouldQueue
{
    use Dispatchable;

    public $tries = 3;
    public $timeout = 30;

    public function __construct(public AIJob $job) {}

    public function handle(WorkspaceGeneratorAgent $workspaceGeneratorAgent): void
    {
        try {
            switch ($this->job->type) {
                case AIJobsType::COLLECTION_WORKSPACE:
                    $workspaceGeneratorAgent->generateCollectionWorkspace($this->job);
                    break;
                case AIJobsType::WORKFLOW_WORKSPACE:
                    $workspaceGeneratorAgent->generateWorkflowWorkspace($this->job);
                    break;
                default:
                    throw new \Exception("Unsupported workspace type: {$this->job->type}");
            }
        } catch (\Throwable $e) {
            logger($e->getMessage());
            $this->job->update(['status' => 'failed']);
        }
    }
}
