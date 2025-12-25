<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Task;
use App\Models\Tasklist;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use App\Http\Requests\TasklistController\{
    StoreTasklistRequest,
    UpdateTasklistRequest,
    ReorderTasksRequest
};

class TasklistController extends Controller
{
    public function store(StoreTasklistRequest $request)
    {
        $workspace = $request->user()
            ->workspaces()
            ->findOrFail($request->workspaceId);

        $nextOrder = ($workspace->tasklists()->max('order') ?? 0) + 1;

        return Tasklist::create([
            'name' => $request->name,
            'workspace_id' => $workspace->id,
            'order' => $nextOrder,
        ]);
    }

    public function update(UpdateTasklistRequest $request, $workspaceId, $tasklistId)
    {
        $tasklist = Tasklist::ownedBy($request->user())
            ->where('workspace_id', $workspaceId)
            ->findOrFail($tasklistId);

        $tasklist->update($request->validated());

        return $tasklist;
    }

    public function delete(Request $request, $tasklistId)
    {
        $user = $request->user();

        DB::transaction(function () use ($user, $tasklistId) {

            $tasklist = Tasklist::ownedBy($user)
                ->findOrFail($tasklistId);

            $workspaceId = $tasklist->workspace_id;
            $deletedOrder = $tasklist->order;

            $tasklist->delete();

            Tasklist::where('workspace_id', $workspaceId)
                ->where('order', '>', $deletedOrder)
                ->decrement('order');
        });

        return response()->noContent();
    }


    public function reorderTasks(ReorderTasksRequest $request)
    {
        $user = $request->user();

        $tasklists = Tasklist::ownedBy($user)
            ->whereIn('id', [
                $request->newTasklistId,
                $request->sourceTasklistId,
            ])
            ->pluck('id');

        if (
            $tasklists->count() !== collect([
                $request->newTasklistId,
                $request->sourceTasklistId,
            ])->unique()->count()
        ) {
            abort(403);
        }

        DB::transaction(function () use ($request, $user) {

            foreach ($request->order as $index => $taskId) {
                Task::ownedBy($user)
                    ->where('id', $taskId)
                    ->update([
                        'tasklist_id' => $request->newTasklistId,
                        'order' => $index + 1,
                    ]);
            }

            if ($request->newTasklistId !== $request->sourceTasklistId) {
                Task::ownedBy($user)
                    ->where('tasklist_id', $request->sourceTasklistId)
                    ->orderBy('order')
                    ->get()
                    ->each(
                        fn($task, $i) =>
                        $task->update(['order' => $i + 1])
                    );
            }
        });

        return response()->json(['success' => true]);
    }
}
