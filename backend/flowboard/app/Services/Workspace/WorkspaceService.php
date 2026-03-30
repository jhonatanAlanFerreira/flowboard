<?php

namespace App\Services\Workspace;

use App\Data\WorkspaceData;
use App\Models\Workspace;

class WorkspaceService
{
    public function persistWorkspace(WorkspaceData $data, int $userId): Workspace
    {
        $workspace = Workspace::create([
            'name' => $data->name,
            'user_id' => $userId,
        ]);

        foreach ($data->lists as $index => $listData) {
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
    }

    public function exportWorkspace(Workspace $workspace)
    {
        $workspace->loadMissing('tasklists.tasks');

        $data = [
            'name' => $workspace->name,
            'lists' => $workspace->tasklists
                ->sortBy('order')
                ->values()
                ->map(function ($list) {
                    return [
                        'name' => $list->name,
                        'tasks' => $list->tasks
                            ->sortBy('order')
                            ->values()
                            ->map(function ($task) {
                                return [
                                    'description' => $task->description,
                                    'done' => $task->done ? "True" : "False"
                                ];
                            }),
                    ];
                }),
        ];

        return response()->json($data);
    }
}
