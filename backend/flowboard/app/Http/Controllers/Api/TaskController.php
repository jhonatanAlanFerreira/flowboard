<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Task;
use Illuminate\Http\Request;
use App\Http\Requests\TaskController\{
    StoreTaskRequest,
    UpdateTaskRequest
};
use App\Models\Tasklist;
use Illuminate\Support\Facades\DB;

class TaskController extends Controller
{
    public function store(StoreTaskRequest $request)
    {
        $user = $request->user();

        $tasklist = Tasklist::ownedBy($user)
            ->findOrFail($request->tasklistId);

        $nextOrder = (Task::where('tasklist_id', $tasklist->id)->max('order') ?? 0) + 1;

        Task::create([
            'description' => $request->description,
            'tasklist_id' => $tasklist->id,
            'order' => $nextOrder,
        ]);

        return response()->json(['success' => true], 201);
    }

    public function update(UpdateTaskRequest $request, $taskId)
    {
        $task = Task::ownedBy($request->user())
            ->findOrFail($taskId);

        $task->update($request->validated());

        return $task;
    }

    public function delete(Request $request, $taskId)
    {
        $user = $request->user();

        DB::transaction(function () use ($user, $taskId) {

            $task = Task::ownedBy($user)->findOrFail($taskId);

            $tasklistId = $task->tasklist_id;
            $deletedOrder = $task->order;

            $task->delete();

            Task::where('tasklist_id', $tasklistId)
                ->where('order', '>', $deletedOrder)
                ->decrement('order');
        });

        return response()->noContent();
    }
}
