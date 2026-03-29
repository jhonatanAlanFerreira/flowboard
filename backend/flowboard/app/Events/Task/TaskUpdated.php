<?php

namespace App\Events\Task;

use App\Models\Task;

class TaskUpdated
{
    public function __construct(public Task $task) {}
}
