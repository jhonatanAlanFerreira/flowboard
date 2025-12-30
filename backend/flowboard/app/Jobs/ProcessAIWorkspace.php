<?php

namespace App\Jobs;

use App\Models\AIJob;
use App\Services\AIWorkspaceService;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;

class ProcessAIWorkspace implements ShouldQueue
{
    use Dispatchable;

    public $timeout = 0;
    public $tries = 1;
    public function __construct(public AIJob $job)
    {
    }

    public function handle(AIWorkspaceService $service): void
    {
        try {
            $result = $service->callAI($this->job->prompt);

            $workspace = $service->persistWorkspace($result, $this->job->user_id);

            $this->job->update([
                'status' => 'done',
                'workspace_id' => $workspace->id,
            ]);
        } catch (\Throwable $e) {
            logger($e->getMessage());
            $this->job->update(['status' => 'failed']);
        }
    }
}
