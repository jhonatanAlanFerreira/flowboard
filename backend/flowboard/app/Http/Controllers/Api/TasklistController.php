<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Task;
use App\Models\Tasklist;
use App\Models\Workspace;
use Illuminate\Http\Request;

class TasklistController extends Controller
{
    public function index(Request $request, $workspaceId)
    {
        return $request->user()
            ->workspaces()
            ->findOrFail($workspaceId)
            ->tasklists()
            ->with('tasks')
            ->get();
    }

    public function storeTasklist(Request $request)
    {
        $request->validate([
            'name' => 'required|string|max:255',
            'workspaceId' => 'required|integer',
        ]);

        $workspace = $request->user()
            ->workspaces()
            ->findOrFail($request->workspaceId);

        $nextOrder = $workspace->tasklists()->max('order') + 1;

        $tasklist = Tasklist::create([
            'name' => $request->name,
            'workspace_id' => $workspace->id,
            'order' => $nextOrder,
        ]);

        return response()->json($tasklist, 201);
    }

    public function storeTask(Request $request)
    {
        Task::create([
            "description" => $request->description,
            "tasklist_id" => $request->tasklistId,
            "order" => 1
        ]);
    }

    public function storeWorkspace(Request $request)
    {
        return Workspace::create([
            "name" => $request->name,
            "user_id" => $request->user()->id
        ]);
    }

    public function deleteTask($taskId)
    {
        Task::where("id", $taskId)->delete();
    }

    public function deleteTasklist($tasklistId)
    {
        Tasklist::where("id", $tasklistId)->delete();
    }

    public function deleteWorkspace($workspaceId)
    {
        Workspace::where("id", $workspaceId)->delete();
    }

    public function changeTaskIsDone($taskId, Request $request)
    {
        Task::where("id", $taskId)->update([
            "done" => $request->done
        ]);
    }

    public function reorderTasklists(Request $request)
    {
        $request->validate([
            'workspaceId' => 'required|integer',
            'order' => 'required|array|min:1',
            'order.*' => 'integer',
        ]);

        $workspace = $request->user()
            ->workspaces()
            ->where('id', $request->workspaceId)
            ->firstOrFail();

        foreach ($request->order as $index => $tasklistId) {
            Tasklist::where('id', $tasklistId)
                ->where('workspace_id', $workspace->id)
                ->update([
                    'order' => $index + 1
                ]);
        }

        return response()->json(['success' => true]);
    }
}
