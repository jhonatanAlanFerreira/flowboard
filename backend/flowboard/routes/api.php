<?php

use App\Http\Controllers\Api\TasklistController;
use App\Http\Controllers\Api\WorkspaceController;
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

Route::middleware('auth:sanctum')
    ->group(function () {
        Route::prefix('me')->group(function () {
            Route::apiResource('workspaces', WorkspaceController::class);
            Route::apiResource('{workspaceId}/tasklists', TasklistController::class);
        });
    });
