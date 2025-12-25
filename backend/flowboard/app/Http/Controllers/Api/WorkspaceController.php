<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Tasklist;
use App\Models\Workspace;
use Illuminate\Http\Request;
use App\Http\Requests\WorkspaceController\{
    IndexWorkspaceRequest,
    StoreWorkspaceRequest,
    UpdateWorkspaceRequest,
    ReorderTasklistsRequest
};

class WorkspaceController extends Controller
{
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

        foreach ($request->order as $index => $tasklistId) {
            Tasklist::where('id', $tasklistId)
                ->where('workspace_id', $workspace->id)
                ->update(['order' => $index + 1]);
        }

        return response()->json(['success' => true]);
    }
}