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
    public function store(Request $request)
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

    public function update(Request $request, $workspaceId, $tasklistId)
    {
        $tasklist = $request->user()->workspaces()->findOrFail($workspaceId)->tasklists()->findOrFail($tasklistId);
        $tasklist->fill($request->all())->save();
        return $tasklist;
    }

    public function delete(Request $request, $tasklistId)
    {
        Tasklist::ownedBy($request->user())
            ->findOrFail($tasklistId)
            ->delete();
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
