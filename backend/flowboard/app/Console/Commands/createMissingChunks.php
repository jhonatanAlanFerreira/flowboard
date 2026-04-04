<?php

namespace App\Console\Commands;

use App\Events\List\TasklistUpdated;
use App\Events\Task\TaskUpdated;
use Illuminate\Console\Command;
use App\Models\Task;
use App\Models\Tasklist;

class CreateMissingChunks extends Command
{
    protected $signature = 'tasks:chunk-missing {--user_id=} {--preview}';
    protected $description = 'Generate missing chunks for tasks and tasklists';

    public function handle()
    {
        $userId = $this->option('user_id');
        $preview = $this->option('preview');

        $taskQuery = Task::query()
            ->where(function ($q) {
                $q->whereDoesntHave('chunk')
                  ->orWhereHas('chunk', function ($query) {
                      $query->withoutEmbedding();
                  });
            })
            ->with(['user', 'tasklist.workspace']);

        if ($userId) {
            $taskQuery->where('user_id', $userId);
            $this->info("Filtering by user_id: {$userId}");
        }

        $tasks = $taskQuery->get();

        $tasklistsQuery = Tasklist::query()
            ->where(function ($q) {
                $q->whereDoesntHave('chunk')
                  ->orWhereHas('chunk', function ($query) {
                      $query->withoutEmbedding();
                  });
            })
            ->with(['user', 'workspace']);

        if ($userId) {
            $tasklistsQuery->where('user_id', $userId);
        }

        $tasklists = $tasklistsQuery->get();

        $userCount = $tasks->pluck('user.id')->unique()->count();
        $workspaceCount = $tasks->pluck('tasklist.workspace.id')->unique()->count();
        $taskCount = $tasks->count();
        $tasklistCount = $tasklists->count();

        $summary = [
            'users' => "$userCount user(s) with chunk issues",
            'workspaces' => "$workspaceCount workspace(s) affected",
            'tasks' => "total of $taskCount tasks with missing chunks",
            'tasklists' => "total of $tasklistCount tasklists with missing chunks",
        ];

        $this->info(json_encode($summary, JSON_PRETTY_PRINT));
        $this->line("");

        if ($preview) {
            $this->info("Preview mode enabled. No events will be dispatched.");
            return;
        }


        $tasks->groupBy('user.id')->each(function ($userTasks) {

            $userName = $userTasks->first()->user->name;
            $this->info("Processing User: {$userName}");

            $userTasks->groupBy(fn ($t) => $t->tasklist->workspace->id)
                ->each(function ($workspaceTasks) {

                    $workspace = $workspaceTasks->first()->tasklist->workspace;
                    $workspaceName = $workspace->name;

                    $this->line("");
                    $this->info("  Workspace: {$workspaceName}");

                    $workspaceTasks->groupBy('tasklist_id')
                        ->each(function ($listTasks) {

                            $listName = $listTasks->first()->tasklist->name;
                            $this->info("    List: {$listName}");

                            foreach ($listTasks->sortBy('order') as $task) {
                                event(new TaskUpdated($task));
                            }
                        });
                });
        });

        $this->line("");
        $this->info("Processing Tasklists (list chunks)");

        $tasklists->groupBy('user.id')->each(function ($userLists) {

            $userName = $userLists->first()->user->name;
            $this->info("Processing User: {$userName}");

            $userLists->groupBy('workspace_id')->each(function ($workspaceLists) {

                $workspace = $workspaceLists->first()->workspace;
                $workspaceName = $workspace->name;

                $this->line("");
                $this->info("  Workspace: {$workspaceName}");

                foreach ($workspaceLists as $list) {
                    $this->info("    List: {$list->name}");

                    event(new TasklistUpdated($list));
                }
            });
        });

        $this->info('');
        $this->info('Missing chunks processed.');
        $this->info('Task chunks and list chunks will be generated via AI API.');
        $this->info('Track progress in Phoenix UI.');
    }
}