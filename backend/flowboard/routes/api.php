<?php

use App\Http\Controllers\Api\AI\AIChunkController;
use App\Http\Controllers\Api\AI\AIDataQuestionController;
use App\Http\Controllers\Api\AI\AIRetrievalController;
use App\Http\Controllers\Api\AI\AIWorkspaceController;
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
    Route::get('/', [LoginController::class, "index"]);
    Route::get('workspace/{workspaceId}/tasklists', [WorkspaceController::class, "index"]);
    Route::get('workspaces', [WorkspaceController::class, "userWorkspaces"]);
    Route::get('workspace/{workspaceId}/export-json', [WorkspaceController::class, "exportWorkspace"]);

    Route::post('workspace', [WorkspaceController::class, "store"]);
    Route::post('workspace/import-json', [WorkspaceController::class, "storeFromJson"]);
    Route::post('tasklist', [TasklistController::class, "store"]);
    Route::post('task', [TaskController::class, "store"]);

    Route::put('workspace/{workspaceId}', [WorkspaceController::class, "update"]);
    Route::put('tasklist/{tasklistId}', [TasklistController::class, "update"]);
    Route::put('task/{taskId}', [TaskController::class, "update"]);
    Route::put('tasklists/reorder', [WorkspaceController::class, "reorderTasklists"]);
    Route::put('tasks/reorder', [TasklistController::class, "reorderTasks"]);
    Route::put('copy-list/{tasklistId}/workspace/{workspaceId}', [TasklistController::class, "copyList"]);
    Route::put('send-task/{taskId}/workspace/{workspaceId}', [TaskController::class, 'sendToWorkspace']);

    Route::delete('workspace/{workspaceId}', [WorkspaceController::class, "delete"]);
    Route::delete('tasklist/{tasklistId}', [TasklistController::class, "delete"]);
    Route::delete('task/{taskId}', [TaskController::class, "delete"]);

    Route::prefix('ai')->group(function () {
        Route::get('/health', [AIWorkspaceController::class, 'checkAiEndpoint']);
        Route::post('/retrieval', [AIRetrievalController::class, 'retrieve']);

        Route::prefix('workspaces')->group(function () {
            Route::post('/', [AIWorkspaceController::class, 'generate']);
            Route::get('/latest', [AIWorkspaceController::class, 'latest']);
        });

        Route::post('/data-question', [AIWorkspaceController::class, 'dataQuestion']);
    });
});

Route::middleware('ai')->prefix('internal/ai')->group(function () {
    Route::post('/workspaces', [AIWorkspaceController::class, 'storeFromAI']);
    Route::put('/chunk/{chunkId}/tags', [AIChunkController::class, 'updateChunkTags']);
    Route::put('/data-question-hydrate', [AIDataQuestionController::class, 'hydrateDataQuestionRetrieval']);
});
