<?php

namespace App\Events\Task;

use App\Models\Task;

class TaskCreated
{
    public function __construct(public Task $task) {}

    public function listId(): int
    {
        return $this->task->tasklist_id;
    }
}
