<?php

namespace Tests\Feature;

use Tests\TestCase;
use App\Models\User;
use App\Models\Workspace;
use App\Models\Tasklist;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tymon\JWTAuth\Facades\JWTAuth;

class TasklistTest extends TestCase
{
    use RefreshDatabase;

    /** @test */
    public function user_can_create_tasklist()
    {
        $user = User::factory()->create();

        $workspace = Workspace::factory()->create([
            'user_id' => $user->id
        ]);

        $response = $this->auth($user)
            ->postJson('/api/me/tasklist', [
                'name' => 'Todo',
                'workspaceId' => $workspace->id
            ]);

        $response->assertStatus(201);

        $this->assertDatabaseHas('tasklists', [
            'name' => 'Todo',
            'workspace_id' => $workspace->id,
            'user_id' => $user->id
        ]);
    }

    /** @test */
    public function user_cannot_create_tasklist_in_another_users_workspace()
    {
        $user = User::factory()->create();
        $otherUser = User::factory()->create();

        $workspace = Workspace::factory()->create([
            'user_id' => $otherUser->id
        ]);

        $response = $this->auth($user)
            ->postJson('/api/me/tasklist', [
                'name' => 'Hack attempt',
                'workspaceId' => $workspace->id
            ]);

        $response->assertStatus(404);
    }

    /** @test */
    public function user_can_update_tasklist()
    {
        $user = User::factory()->create();

        $tasklist = Tasklist::factory()->create([
            'user_id' => $user->id
        ]);

        $response = $this->auth($user)
            ->putJson("/api/me/tasklist/{$tasklist->id}", [
                'name' => 'Updated Name'
            ]);

        $response->assertStatus(200);

        $this->assertDatabaseHas('tasklists', [
            'id' => $tasklist->id,
            'name' => 'Updated Name'
        ]);
    }

    /** @test */
    public function user_cannot_update_another_users_tasklist()
    {
        $user = User::factory()->create();
        $otherUser = User::factory()->create();

        $tasklist = Tasklist::factory()->create([
            'user_id' => $otherUser->id
        ]);

        $response = $this->auth($user)
            ->putJson("/api/me/tasklist/{$tasklist->id}", [
                'name' => 'Hacked'
            ]);

        $response->assertStatus(404);
    }

    /** @test */
    public function user_can_delete_tasklist()
    {
        $user = User::factory()->create();

        $tasklist = Tasklist::factory()->create([
            'user_id' => $user->id
        ]);

        $response = $this->auth($user)
            ->deleteJson("/api/me/tasklist/{$tasklist->id}");

        $response->assertStatus(204);

        $this->assertDatabaseMissing('tasklists', [
            'id' => $tasklist->id
        ]);
    }

    /** @test */
    public function user_cannot_delete_another_users_tasklist()
    {
        $user = User::factory()->create();
        $otherUser = User::factory()->create();

        $tasklist = Tasklist::factory()->create([
            'user_id' => $otherUser->id
        ]);

        $response = $this->auth($user)
            ->deleteJson("/api/me/tasklist/{$tasklist->id}");

        $response->assertStatus(404);
    }

    /** @test */
    public function user_can_copy_tasklist_to_another_workspace()
    {
        $user = User::factory()->create();

        $workspace1 = Workspace::factory()->create([
            'user_id' => $user->id
        ]);

        $workspace2 = Workspace::factory()->create([
            'user_id' => $user->id
        ]);

        $tasklist = Tasklist::factory()->create([
            'workspace_id' => $workspace1->id,
            'user_id' => $user->id
        ]);

        $response = $this->auth($user)
            ->putJson("/api/me/copy-list/{$tasklist->id}/workspace/{$workspace2->id}");

        $response->assertStatus(201);

        $this->assertDatabaseHas('tasklists', [
            'workspace_id' => $workspace2->id,
            'user_id' => $user->id
        ]);
    }
}
