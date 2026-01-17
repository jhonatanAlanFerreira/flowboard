<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Task;
use App\Models\Tasklist;
use App\Services\OrderService;
use Illuminate\Http\Request;
use App\Http\Requests\TasklistController\{
    StoreTasklistRequest,
    UpdateTasklistRequest,
    ReorderTasksRequest
};

class TasklistController extends Controller
{
    public function __construct(
        private OrderService $orderService
    ) {
    }

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
            'user_id' => $request->user()->id
        ]);
    }

    public function update(UpdateTasklistRequest $request, $tasklistId)
    {
        $tasklist = Tasklist::ownedBy($request->user())
            ->findOrFail($tasklistId);

        $tasklist->update($request->validated());

        return $tasklist;
    }

    public function delete(Request $request, $tasklistId)
    {
        $tasklist = Tasklist::ownedBy($request->user())
            ->findOrFail($tasklistId);

        $this->orderService->deleteAndFixOrder(
            $tasklist,
            'workspace_id'
        );

        return response()->noContent();
    }

    public function reorderTasks(ReorderTasksRequest $request)
    {
        $this->assertTasklistsOwnedByUser(
            $request->user(),
            $request->sourceTasklistId,
            $request->newTasklistId
        );

        $this->orderService->moveAndReorder(
            Task::class,
            'tasklist_id',
            $request->sourceTasklistId,
            $request->newTasklistId,
            $request->order
        );

        return response()->json(['success' => true]);
    }

    private function assertTasklistsOwnedByUser(
        $user,
        int $sourceTasklistId,
        int $targetTasklistId
    ): void {
        $tasklistIds = collect([$sourceTasklistId, $targetTasklistId])
            ->unique()
            ->values();

        $ownedCount = Tasklist::ownedBy($user)
            ->whereIn('id', $tasklistIds)
            ->count();

        if ($ownedCount !== $tasklistIds->count()) {
            abort(403, 'You do not own one or more of the tasklists involved.');
        }
    }

}
