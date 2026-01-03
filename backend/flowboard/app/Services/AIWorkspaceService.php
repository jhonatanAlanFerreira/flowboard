<?php

namespace App\Services;

use App\Models\Workspace;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\DB;

class AIWorkspaceService
{
    public function callAI(string $prompt): array
    {
        $response = Http::timeout(0)
            ->connectTimeout(0)
            ->post(config('services.ai.endpoint') . '/generate-workspace', [
                'prompt' => $prompt,
            ]);

        if (!$response->successful()) {
            logger()->error('AI API failed', [
                'status' => $response->status(),
                'body' => $response->body(),
            ]);

            throw new \RuntimeException('AI API failed');
        }

        return $response->json();
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
                ]);

                foreach ($listData['tasks'] as $taskIndex => $taskData) {
                    $list->tasks()->create([
                        'description' => $taskData['description'],
                        'order' => $taskIndex + 1,
                        'done' => false,
                    ]);
                }
            }

            return $workspace;
        });
    }
}
