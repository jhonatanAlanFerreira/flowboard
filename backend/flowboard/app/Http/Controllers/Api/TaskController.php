<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Task;
use Illuminate\Http\Request;

class TaskController extends Controller
{
    public function store(Request $request)
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

    public function update(Request $request, $taskId)
    {
        $task = Task::ownedBy($request->user())->findOrFail($taskId);
        return $task->update($request->all());
    }

    public function delete($taskId)
    {
        Task::where("id", $taskId)->delete();
    }
}
