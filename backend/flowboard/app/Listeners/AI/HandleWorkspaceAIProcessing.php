<?php

namespace App\Listeners\AI;

use App\Events\Workspace\WorkspaceCreated;
use App\Events\Workspace\WorkspaceDeleted;
use App\Events\Workspace\WorkspaceUpdated;
use App\Jobs\AI\Task\DeleteTaskChunksFromWorkspaceJob;
use App\Jobs\AI\Workspace\GenerateWorkspaceChunkJob;

class HandleWorkspaceAIProcessing
{
    public function handle($event): void
    {
        if ($event instanceof WorkspaceCreated) {
            GenerateWorkspaceChunkJob::dispatch($event->workspace);
        }

        if ($event instanceof WorkspaceUpdated) {
            GenerateWorkspaceChunkJob::dispatch($event->workspace);
        }

        if ($event instanceof WorkspaceDeleted) {
            DeleteTaskChunksFromWorkspaceJob::dispatch($event->workspace->id);
        }
    }
}
