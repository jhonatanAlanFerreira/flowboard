<?php

namespace Tests\Feature;

use Tests\TestCase;
use App\Models\User;
use App\Models\Workspace;
use App\Models\Tasklist;
use App\Models\Task;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tymon\JWTAuth\Facades\JWTAuth;

class ReorderTest extends TestCase
{
    use RefreshDatabase;

    /** @test */
    public function user_can_reorder_tasklists()
    {
        $user = User::factory()->create();

        $workspace = Workspace::factory()->create([
            'user_id' => $user->id
        ]);

        $list1 = Tasklist::factory()->create([
            'workspace_id' => $workspace->id,
            'user_id' => $user->id,
            'order' => 1
        ]);

        $list2 = Tasklist::factory()->create([
            'workspace_id' => $workspace->id,
            'user_id' => $user->id,
            'order' => 2
        ]);

        $payload = [
            "workspaceId" => $workspace->id,
            "order" => [$list2->id, $list1->id]
        ];

        $response = $this->auth($user)
            ->putJson('/api/me/tasklists/reorder', $payload);

        $response->assertStatus(200);

        $this->assertDatabaseHas('tasklists', [
            'id' => $list1->id,
            'order' => 2
        ]);

        $this->assertDatabaseHas('tasklists', [
            'id' => $list2->id,
            'order' => 1
        ]);
    }

    /** @test */
    public function user_can_reorder_tasks_within_tasklist()
    {
        $user = User::factory()->create();

        $tasklist = Tasklist::factory()->create([
            'user_id' => $user->id
        ]);

        $task1 = Task::factory()->create([
            'tasklist_id' => $tasklist->id,
            'user_id' => $user->id,
            'order' => 1
        ]);

        $task2 = Task::factory()->create([
            'tasklist_id' => $tasklist->id,
            'user_id' => $user->id,
            'order' => 2
        ]);

        $payload = [
            "newTasklistId" => $tasklist->id,
            "sourceTasklistId" => $tasklist->id,
            "order" => [$task2->id, $task1->id]
        ];

        $response = $this->auth($user)
            ->putJson('/api/me/tasks/reorder', $payload);

        $response->assertStatus(200);

        $this->assertDatabaseHas('tasks', [
            'id' => $task1->id,
            'order' => 2
        ]);

        $this->assertDatabaseHas('tasks', [
            'id' => $task2->id,
            'order' => 1
        ]);
    }

    /** @test */
    public function user_cannot_reorder_tasklists_from_another_user()
    {
        $user = User::factory()->create();
        $otherUser = User::factory()->create();

        $workspace = Workspace::factory()->create([
            'user_id' => $otherUser->id
        ]);

        $list1 = Tasklist::factory()->create([
            'workspace_id' => $workspace->id,
            'user_id' => $otherUser->id,
            'order' => 1
        ]);

        $list2 = Tasklist::factory()->create([
            'workspace_id' => $workspace->id,
            'user_id' => $otherUser->id,
            'order' => 2
        ]);

        $payload = [
            "workspaceId" => $workspace->id,
            "order" => [$list2->id, $list1->id]
        ];

        $response = $this->auth($user)
            ->putJson('/api/me/tasklists/reorder', $payload);

        $response->assertStatus(404);
    }

    /** @test */
    public function reorder_fails_with_invalid_task_id()
    {
        $user = User::factory()->create();

        $tasklist = Tasklist::factory()->create([
            'user_id' => $user->id
        ]);

        $payload = [
            "newTasklistId" => $tasklist->id,
            "sourceTasklistId" => $tasklist->id,
            "order" => [1, 2]
        ];

        $response = $this->auth($user)
            ->putJson('/api/me/tasks/reorder', $payload);

        $response->assertStatus(422);
    }
}
