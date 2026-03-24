<?php

namespace Tests\Feature;

use Tests\TestCase;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;

class AuthTest extends TestCase
{
    use RefreshDatabase;

    /** @test */
    public function unauthenticated_user_cannot_access_protected_routes()
    {
        $this->getJson('/api/me/workspaces')
            ->assertStatus(401);

        $this->postJson('/api/me/workspace', [
            'name' => 'Test Workspace'
        ])->assertStatus(401);
    }

    /** @test */
    public function authenticated_user_can_access_protected_routes()
    {
        $user = User::factory()->create();

        $this->actingAs($user, 'api')
            ->getJson('/api/me/workspaces')
            ->assertStatus(200);
    }

    /** @test */
    public function user_cannot_access_another_users_workspace()
    {
        $user = User::factory()->create();
        $otherUser = User::factory()->create();

        $workspace = \App\Models\Workspace::factory()->create([
            'user_id' => $otherUser->id
        ]);

        $this->actingAs($user, 'api')
            ->getJson("/api/me/workspace/{$workspace->id}/tasklists")
            ->assertStatus(404);
    }
}
