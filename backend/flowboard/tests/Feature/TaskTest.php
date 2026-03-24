<?php

namespace Tests\Feature;

use Tests\TestCase;
use App\Models\User;
use App\Models\Workspace;
use App\Models\Tasklist;
use App\Models\Task;
use Illuminate\Foundation\Testing\RefreshDatabase;

class TaskTest extends TestCase
{
    use RefreshDatabase;

    /** @test */
    public function user_can_create_task()
    {
        $user = User::factory()->create();

        $tasklist = Tasklist::factory()->create([
            'user_id' => $user->id
        ]);

        $response = $this->auth($user)
            ->postJson('/api/me/task', [
                'description' => 'New Task',
                'tasklistId' => $tasklist->id
            ]);

        $response->assertStatus(201);

        $this->assertDatabaseHas('tasks', [
            'description' => 'New Task',
            'tasklist_id' => $tasklist->id,
            'user_id' => $user->id
        ]);
    }

    /** @test */
    public function user_cannot_create_task_in_another_users_tasklist()
    {
        $user = User::factory()->create();
        $otherUser = User::factory()->create();

        $tasklist = Tasklist::factory()->create([
            'user_id' => $otherUser->id
        ]);

        $response = $this->auth($user)
            ->postJson('/api/me/task', [
                'description' => 'Hack attempt',
                'tasklistId' => $tasklist->id
            ]);

        $response->assertStatus(404);
    }

    /** @test */
    public function user_can_update_task()
    {
        $user = User::factory()->create();

        $task = Task::factory()->create([
            'user_id' => $user->id
        ]);

        $response = $this->auth($user)
            ->putJson("/api/me/task/{$task->id}", [
                'description' => 'Updated Task'
            ]);

        $response->assertStatus(200);

        $this->assertDatabaseHas('tasks', [
            'id' => $task->id,
            'description' => 'Updated Task'
        ]);
    }

    /** @test */
    public function user_cannot_update_another_users_task()
    {
        $user = User::factory()->create();
        $otherUser = User::factory()->create();

        $task = Task::factory()->create([
            'user_id' => $otherUser->id
        ]);

        $response = $this->auth($user)
            ->putJson("/api/me/task/{$task->id}", [
                'description' => 'Hacked'
            ]);

        $response->assertStatus(404);
    }

    /** @test */
    public function user_can_delete_task()
    {
        $user = User::factory()->create();

        $task = Task::factory()->create([
            'user_id' => $user->id
        ]);

        $response = $this->auth($user)
            ->deleteJson("/api/me/task/{$task->id}");

        $response->assertStatus(204);

        $this->assertDatabaseMissing('tasks', [
            'id' => $task->id
        ]);
    }

    /** @test */
    public function user_cannot_delete_another_users_task()
    {
        $user = User::factory()->create();
        $otherUser = User::factory()->create();

        $task = Task::factory()->create([
            'user_id' => $otherUser->id
        ]);

        $response = $this->auth($user)
            ->deleteJson("/api/me/task/{$task->id}");

        $response->assertStatus(404);
    }

    /** @test */
    public function user_can_move_task_to_another_workspace()
    {
        $user = User::factory()->create();

        $workspace1 = Workspace::factory()->create([
            'user_id' => $user->id
        ]);

        $workspace2 = Workspace::factory()->create([
            'user_id' => $user->id
        ]);

        $tasklist1 = Tasklist::factory()->create([
            'workspace_id' => $workspace1->id,
            'user_id' => $user->id
        ]);

        $task = Task::factory()->create([
            'tasklist_id' => $tasklist1->id,
            'user_id' => $user->id,
            'description' => 'Original Task'
        ]);

        $response = $this->auth($user)
            ->putJson("/api/me/send-task/{$task->id}/workspace/{$workspace2->id}");

        $response->assertStatus(200);

        // ✅ 1. Old task should be deleted
        $this->assertDatabaseMissing('tasks', [
            'id' => $task->id
        ]);

        // ✅ 2. Imported list exists
        $this->assertDatabaseHas('tasklists', [
            'workspace_id' => $workspace2->id,
            'name' => 'Imported Tasks'
        ]);

        $importedList = Tasklist::where('workspace_id', $workspace2->id)
            ->where('name', 'Imported Tasks')
            ->first();

        // ✅ 3. New task exists in imported list
        $this->assertDatabaseHas('tasks', [
            'tasklist_id' => $importedList->id,
            'description' => 'Original Task'
        ]);
    }
}
