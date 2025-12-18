<?php

use App\Http\Controllers\Api\TasklistController;
use App\Http\Controllers\Api\WorkspaceController;
use App\Http\Controllers\LoginController;
use Illuminate\Http\Request;
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
    Route::get('workspaces', [WorkspaceController::class, "index"]);
    Route::get('workspace/{workspaceId}/tasklists', [TasklistController::class, "index"]);

    Route::post('tasklist', [TasklistController::class, "storeTasklist"]);
    Route::post('task', [TasklistController::class, "storeTask"]);
    Route::post('workspace', [TasklistController::class, "storeWorkspace"]);

    Route::delete('task/{taskId}', [TasklistController::class, "deleteTask"]);
    Route::delete('tasklist/{tasklistId}', [TasklistController::class, "deleteTasklist"]);
    Route::delete('workspace/{workspaceId}', [TasklistController::class, "deleteWorkspace"]);
});