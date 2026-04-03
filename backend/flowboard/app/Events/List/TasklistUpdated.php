<?php

namespace App\Events\List;

use App\Models\Tasklist;

class TasklistUpdated
{
    public function __construct(public Tasklist $tasklist) {}
}
