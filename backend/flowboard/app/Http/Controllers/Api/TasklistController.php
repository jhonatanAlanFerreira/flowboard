<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;

class TasklistController extends Controller
{
    public function index(Request $request, $workspaceId)
    {
        return $request->user()->workspaces()->findOrFail($workspaceId)->tasklists->load('tasks');
    }
}
