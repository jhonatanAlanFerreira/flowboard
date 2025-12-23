<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Task;
use App\Models\Tasklist;
use App\Models\Workspace;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

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
        $request->validate([
            'description' => 'required|string',
            'tasklistId' => 'required|integer',
        ]);

        $tasklist = $request->user()
            ->workspaces()
            ->join('tasklists', 'tasklists.workspace_id', '=', 'workspaces.id')
            ->where('tasklists.id', $request->tasklistId)
            ->select('tasklists.id')
            ->firstOrFail();

        $nextOrder = Task::where('tasklist_id', $tasklist->id)->max('order') ?? 0;

        Task::create([
            'description' => $request->description,
            'tasklist_id' => $tasklist->id,
            'order' => $nextOrder + 1,
        ]);

        return response()->json(['success' => true], 201);
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

    public function reorderTasks(Request $request)
    {
        $request->validate([
            'newTasklistId' => 'required|integer',
            'sourceTasklistId' => 'required|integer',
            'order' => 'required|array|min:1',
            'order.*' => 'integer',
        ]);

        $tasklistIds = collect([
            $request->newTasklistId,
            $request->sourceTasklistId,
        ])->unique()->values();

        $tasklists = $request->user()
            ->workspaces()
            ->join('tasklists', 'tasklists.workspace_id', '=', 'workspaces.id')
            ->whereIn('tasklists.id', $tasklistIds)
            ->select('tasklists.id')
            ->get();

        if ($tasklists->count() !== $tasklistIds->count()) {
            abort(403);
        }

        DB::transaction(function () use ($request) {
            foreach ($request->order as $index => $taskId) {
                Task::where('id', $taskId)->update([
                    'tasklist_id' => $request->newTasklistId,
                    'order' => $index + 1,
                ]);
            }

            if ($request->newTasklistId !== $request->sourceTasklistId) {
                $sourceTasks = Task::where('tasklist_id', $request->sourceTasklistId)
                    ->orderBy('order')
                    ->get();

                foreach ($sourceTasks as $index => $task) {
                    $task->update([
                        'order' => $index + 1,
                    ]);
                }
            }
        });

        return response()->json(['success' => true]);
    }

}
