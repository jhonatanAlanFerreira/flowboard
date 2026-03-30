<?php

namespace App\Events\List;

use App\Models\Tasklist;

class TasklistDeleted
{
    public function __construct(public Tasklist $tasklist) {}
}
