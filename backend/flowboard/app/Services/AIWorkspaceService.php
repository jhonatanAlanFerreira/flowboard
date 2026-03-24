<?php

namespace App\Services;

use App\Models\Workspace;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class AIWorkspaceService
{
    public function callAI(string $prompt): array
    {
        $maxAttempts = 5;
        $attempt = 0;

        while ($attempt < $maxAttempts) {
            try {
                $attempt++;

                $response = Http::timeout(0)
                    ->connectTimeout(0)
                    ->post(config('services.ai.endpoint') . '/generate-workspace', [
                        'prompt' => $prompt,
                    ]);

                if ($response->successful()) {
                    return $response->json();
                }

                Log::warning('AI API responded with error', [
                    'attempt' => $attempt,
                    'status' => $response->status(),
                    'body' => $response->body(),
                ]);
            } catch (\Throwable $e) {
                Log::warning('AI API request failed', [
                    'attempt' => $attempt,
                    'error' => $e->getMessage(),
                ]);
            }

            sleep(pow(2, $attempt));
        }

        Log::error('AI API completely unavailable after retries');

        throw new \RuntimeException('AI API is not responding');
    }

    public function persistWorkspace(array $data, $userId): Workspace
    {
        return DB::transaction(function () use ($data, $userId) {
            $workspace = Workspace::create([
                'name' => $data['workflow']['name'],
                'user_id' => $userId,
            ]);

            foreach ($data['workflow']['lists'] as $index => $listData) {
                $list = $workspace->tasklists()->create([
                    'name' => $listData['name'],
                    'order' => $index + 1,
                    'user_id' => $userId,
                ]);

                foreach ($listData['tasks'] as $taskIndex => $taskData) {
                    $list->tasks()->create([
                        'description' => $taskData['description'],
                        'order' => $taskIndex + 1,
                        'done' => false,
                        'user_id' => $userId,
                    ]);
                }
            }

            return $workspace;
        });
    }
}
