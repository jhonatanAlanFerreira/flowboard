<?php

namespace App\Jobs\AI;

use App\Models\AIJob;
use App\Services\AI\Agents\SearchStrategistAgent;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;

class ProcessUserQuestionJob implements ShouldQueue
{
    use Dispatchable;

    public $tries = 3;
    public $timeout = 30;

    public function __construct(public AIJob $job) {}

    public function handle(SearchStrategistAgent $searchStrategistAgent): void
    {
        try {
            $searchStrategistAgent->extractSearchIntent($this->job);
        } catch (\Throwable $e) {
            logger($e->getMessage());
            $this->job->update(['status' => 'failed']);
        }
    }
}
