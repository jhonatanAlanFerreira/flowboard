<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Task;
use App\Models\Tasklist;
use App\Services\OrderService;
use Illuminate\Http\Request;
use App\Http\Requests\TaskController\{
    StoreTaskRequest,
    UpdateTaskRequest
};

class TaskController extends Controller
{
    public function __construct(
        private OrderService $orderService
    ) {
    }

    public function store(StoreTaskRequest $request)
    {
        $tasklist = Tasklist::ownedBy($request->user())
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
        $task = Task::ownedBy($request->user())
            ->findOrFail($taskId);

        $this->orderService->deleteAndFixOrder(
            $task,
            'tasklist_id'
        );

        return response()->noContent();
    }
}
