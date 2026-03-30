<?php

namespace App\Events\Workspace;

use App\Models\Workspace;

class WorkspaceDeleted
{
    public function __construct(public Workspace $workspace) {}
}
