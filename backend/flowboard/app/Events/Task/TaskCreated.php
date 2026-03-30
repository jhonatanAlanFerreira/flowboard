<?php

namespace App\Events\Task;

use App\Models\Task;

class TaskCreated
{
    public function __construct(public Task $task) {}
}
