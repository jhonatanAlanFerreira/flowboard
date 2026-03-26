<?php

namespace App\Listeners\AI;

use App\Events\Task\TaskCreated;
use App\Jobs\AI\GenerateTaskChunkJob;

class HandleTaskAIProcessing
{
    public function handle($event): void
    {
        if ($event instanceof TaskCreated) {
            GenerateTaskChunkJob::dispatch($event->task);
        }

        // if ($event instanceof TaskUpdated) {
        //     GenerateTaskChunkJob::dispatch($event->task);
        // }

        // if ($event instanceof TaskDeleted) {
        //     DeleteTaskChunkJob::dispatch($event->taskId);
        // }


        // MarkListDirtyJob::dispatch($event->listId);
        // MarkWorkspaceDirtyJob::dispatch($event->listId);
    }
}
