<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Tasklist;
use App\Models\Workspace;
use Illuminate\Http\Request;
use App\Services\OrderService;
use App\Http\Requests\WorkspaceController\{
    IndexWorkspaceRequest,
    StoreWorkspaceRequest,
    UpdateWorkspaceRequest,
    ReorderTasklistsRequest
};

class WorkspaceController extends Controller
{
    public function __construct(
        private OrderService $orderService
    ) {
    }

    public function index(IndexWorkspaceRequest $request, $workspaceId)
    {
        return $request->user()
            ->workspaces()
            ->findOrFail($workspaceId)
            ->tasklists()
            ->with('tasks')
            ->get();
    }

    public function userWorkspaces(Request $request)
    {
        return $request->user()->workspaces;
    }

    public function store(StoreWorkspaceRequest $request)
    {
        return Workspace::create([
            'name' => $request->validated()['name'],
            'user_id' => $request->user()->id,
        ]);
    }

    public function update(UpdateWorkspaceRequest $request, $workspaceId)
    {
        $workspace = $request->user()->workspaces()->findOrFail($workspaceId);
        $workspace->update($request->validated());

        return $workspace;
    }

    public function delete(Request $request, $workspaceId)
    {
        $request->user()->workspaces()->findOrFail($workspaceId)->delete();
        return response()->noContent();
    }

    public function reorderTasklists(ReorderTasklistsRequest $request)
    {
        $workspace = $request->user()
            ->workspaces()
            ->findOrFail($request->workspaceId);

        $this->assertTasklistsBelongToWorkspace(
            $workspace->id,
            $request->order
        );

        $this->orderService->reorder(
            Tasklist::class,
            $request->order,
            ['workspace_id' => $workspace->id]
        );

        return response()->json(['success' => true]);
    }

    private function assertTasklistsBelongToWorkspace(
        int $workspaceId,
        array $tasklistIds
    ): void {
        $uniqueIds = collect($tasklistIds)->unique()->values();

        $count = Tasklist::where('workspace_id', $workspaceId)
            ->whereIn('id', $uniqueIds)
            ->count();

        if ($count !== $uniqueIds->count()) {
            abort(403, 'One or more tasklists do not belong to this workspace.');
        }
    }
}
