<?php

namespace App\Events\Task;

use App\Models\Task;

class TaskDeleted
{
    public function __construct(public Task $task) {}
}
