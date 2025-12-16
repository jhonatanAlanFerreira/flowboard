<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Task;
use App\Models\Tasklist;
use Illuminate\Http\Request;

class TasklistController extends Controller
{
    public function index(Request $request, $workspaceId)
    {
        return $request->user()->workspaces()->findOrFail($workspaceId)->tasklists->load('tasks');
    }

    public function storeTasklist(Request $request)
    {
        Tasklist::create([
            "name" => $request->name,
            "workspace_id" => $request->workspaceId,
            "order" => 1
        ]);
    }

    public function storeTask(Request $request)
    {
        Task::create([
            "description" => $request->description,
            "tasklist_id" => $request->tasklistId,
            "order" => 1
        ]);
    }
}
