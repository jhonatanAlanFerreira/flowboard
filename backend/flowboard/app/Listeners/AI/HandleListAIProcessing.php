<?php

namespace App\Listeners\AI;

use App\Events\List\TasklistCreated;
use App\Events\List\TasklistUpdated;
use App\Jobs\AI\List\GenerateListChunkJob;

class HandleListAIProcessing
{
    public function handle($event): void
    {
        if ($event instanceof TasklistCreated) {
            GenerateListChunkJob::dispatch($event->tasklist);
        }

        if ($event instanceof TasklistUpdated) {
            GenerateListChunkJob::dispatch($event->tasklist);
        }
    }
}
