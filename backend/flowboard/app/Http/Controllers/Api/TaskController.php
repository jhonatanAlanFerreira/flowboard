<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Task;
use Illuminate\Http\Request;

class TaskController extends Controller
{
    public function update(Request $request, $taskId)
    {
        $task = Task::ownedBy($request->user())->findOrFail($taskId);
        return $task->update($request->all());
    }
}
