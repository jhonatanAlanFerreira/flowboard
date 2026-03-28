<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class VerifyAISecret
{
    public function handle(Request $request, Closure $next)
    {
        $secret = $request->header('X-AI-SECRET') ?? $request->input('ai_secret');

        if (!$secret || $secret !== config('ai.ai_api_secret')) {
            return response()->json(['error' => 'Unauthorized'], 401);
        }

        return $next($request);
    }
}
