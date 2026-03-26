<?php

namespace App\Http\Controllers\Api;

use App\Events\Task\TaskCreated;
use App\Http\Controllers\Controller;
use App\Models\Task;
use App\Models\Tasklist;
use App\Services\OrderService;
use Illuminate\Http\Request;
use App\Http\Requests\TaskController\{
    StoreTaskRequest,
    UpdateTaskRequest
};
use Illuminate\Support\Facades\DB;

class TaskController extends Controller
{
    public function __construct(
        private OrderService $orderService
    ) {}

    public function store(StoreTaskRequest $request)
    {
        $tasklist = Tasklist::ownedBy($request->user())
            ->findOrFail($request->tasklistId);

        if ($tasklist->done_order === 'bottom') {
            Task::where('tasklist_id', $tasklist->id)->increment('order');
            $order = 1;
        } else {
            $order = (Task::where('tasklist_id', $tasklist->id)->max('order') ?? 0) + 1;
        }

        $task = Task::create([
            'description' => $request->description,
            'tasklist_id' => $tasklist->id,
            'order' => $order,
            'user_id' => $request->user()->id
        ]);

        event(new TaskCreated($task));

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

    public function sendToWorkspace(Request $request, $taskId, $workspaceId)
    {
        $user = $request->user();
        $task = Task::ownedBy($user)->findOrFail($taskId);
        $workspace = $user->workspaces()->findOrFail($workspaceId);

        $importedList = Tasklist::where('workspace_id', $workspace->id)
            ->where('user_id', $user->id)
            ->where('name', 'Imported Tasks')
            ->first();

        if (!$importedList) {
            $nextOrder = ($workspace->tasklists()->max('order') ?? 0) + 1;

            $importedList = Tasklist::create([
                'name' => 'Imported Tasks',
                'workspace_id' => $workspace->id,
                'order' => $nextOrder,
                'user_id' => $user->id,
            ]);
        }

        $nextTaskOrder = ($importedList->tasks()->max('order') ?? 0) + 1;

        DB::transaction(function () use ($task, $importedList, $nextTaskOrder) {

            Task::create([
                'description' => $task->description,
                'tasklist_id' => $importedList->id,
                'order' => $nextTaskOrder,
                'user_id' => $task->user_id,
                'done' => $task->done
            ]);

            $this->orderService->deleteAndFixOrder(
                $task,
                'tasklist_id'
            );
        });

        return response()->json(['success' => true]);
    }
}
