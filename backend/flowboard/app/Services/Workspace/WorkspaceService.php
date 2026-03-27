<?php

namespace App\Services\Workspace;

use App\Models\Workspace;
use Illuminate\Support\Facades\DB;

class WorkspaceService
{
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
