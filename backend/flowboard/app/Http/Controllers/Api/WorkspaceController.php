<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Tasklist;
use App\Models\Workspace;
use Illuminate\Http\Request;

class WorkspaceController extends Controller
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
    public function userWorkspaces(Request $request)
    {
        return $request->user()->workspaces;
    }

    public function store(Request $request)
    {
        return Workspace::create([
            "name" => $request->name,
            "user_id" => $request->user()->id
        ]);
    }

    public function update(Request $request, $workspaceId)
    {
        $workspace = $request->user()->workspaces()->findOrFail($workspaceId);
        $workspace->fill($request->all())->save();
        return $workspace;
    }

    public function delete(Request $request, $workspaceId)
    {
        $request->user()->workspaces()->findOrFail($workspaceId)->delete();
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
}
