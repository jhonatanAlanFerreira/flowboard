<?php

namespace App\Listeners\AI;

use App\Events\List\TasklistDeleted;
use App\Events\Task\TaskCreated;
use App\Events\Task\TaskDeleted;
use App\Events\Task\TaskUpdated;
use App\Events\Workspace\WorkspaceDeleted;
use App\Jobs\AI\DeleteTaskChunkJob;
use App\Jobs\AI\DeleteTaskChunksFromListJob;
use App\Jobs\AI\DeleteTaskChunksFromWorkspaceJob;
use App\Jobs\AI\GenerateTaskChunkJob;

class HandleTaskAIProcessing
{
    public function handle($event): void
    {
        if ($event instanceof TaskCreated) {
            GenerateTaskChunkJob::dispatch($event->task);
        }

        if ($event instanceof TaskUpdated) {
            GenerateTaskChunkJob::dispatch($event->task);
        }

        if ($event instanceof TaskDeleted && $event->task->chunk) {
            DeleteTaskChunkJob::dispatch($event->task->chunk->id);
        }

        if ($event instanceof WorkspaceDeleted) {
            DeleteTaskChunksFromWorkspaceJob::dispatch($event->workspace->id);
        }

        if ($event instanceof TasklistDeleted) {
            DeleteTaskChunksFromListJob::dispatch($event->tasklist->id);
        }
    }
}
