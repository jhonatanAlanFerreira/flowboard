<?php

namespace App\Events\Workspace;

use App\Models\Workspace;

class WorkspaceCreated
{
    public function __construct(public Workspace $workspace) {}
}
