<?php

use App\Http\Controllers\Api\LoginController;
use App\Http\Controllers\Api\TaskController;
use App\Http\Controllers\Api\TasklistController;
use App\Http\Controllers\Api\WorkspaceController;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\RegisterController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "api" middleware group. Make something great!
|
*/

Route::post('/register', [RegisterController::class, 'register']);
Route::post('/login', [LoginController::class, 'authenticate']);

Route::middleware('auth:api')->prefix('me')->group(function () {
    Route::get('workspace/{workspaceId}/tasklists', [WorkspaceController::class, "index"]);
    Route::get('workspaces', [WorkspaceController::class, "userWorkspaces"]);

    Route::post('workspace', [WorkspaceController::class, "store"]);
    Route::post('tasklist', [TasklistController::class, "store"]);
    Route::post('task', [TaskController::class, "store"]);

    Route::put('workspace/{workspaceId}', [WorkspaceController::class, "update"]);
    Route::put('task/{taskId}', [TaskController::class, "update"]);
    Route::put('tasklists/reorder', [WorkspaceController::class, "reorderTasklists"]);
    Route::put('tasks/reorder', [TasklistController::class, "reorderTasks"]);

    Route::delete('workspace/{workspaceId}', [WorkspaceController::class, "delete"]);
    Route::delete('tasklist/{tasklistId}', [TasklistController::class, "delete"]);
    Route::delete('task/{taskId}', [TaskController::class, "delete"]);
});