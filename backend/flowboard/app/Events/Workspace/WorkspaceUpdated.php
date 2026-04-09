<?php

namespace App\Events\Workspace;

use App\Models\Workspace;

class WorkspaceUpdated
{
    public function __construct(public Workspace $workspace) {}
}
