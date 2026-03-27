<?php

namespace Tests\Feature;

use Tests\TestCase;
use App\Models\User;
use App\Models\Workspace;
use Illuminate\Foundation\Testing\RefreshDatabase;

class WorkspaceTest extends TestCase
{
    use RefreshDatabase;

    /** @test */
    public function user_can_create_workspace()
    {
        $user = User::factory()->create();

        $response = $this->auth($user)
            ->postJson('/api/me/workspace', [
                'name' => 'My Workspace'
            ]);

        $response->assertStatus(201);

        $this->assertDatabaseHas('workspaces', [
            'name' => 'My Workspace',
            'user_id' => $user->id
        ]);
    }

    /** @test */
    public function user_can_list_only_their_workspaces()
    {
        $user = User::factory()->create();
        $otherUser = User::factory()->create();

        Workspace::factory()->create(['user_id' => $user->id]);
        Workspace::factory()->create(['user_id' => $otherUser->id]);

        $response = $this->auth($user)
            ->getJson('/api/me/workspaces');

        $response->assertStatus(200)
            ->assertJsonCount(1); // only user's workspace
    }

    /** @test */
    public function user_can_update_workspace()
    {
        $user = User::factory()->create();

        $workspace = Workspace::factory()->create([
            'user_id' => $user->id
        ]);

        $response = $this->auth($user)
            ->putJson("/api/me/workspace/{$workspace->id}", [
                'name' => 'Updated Workspace'
            ]);

        $response->assertStatus(200);

        $this->assertDatabaseHas('workspaces', [
            'id' => $workspace->id,
            'name' => 'Updated Workspace'
        ]);
    }

    /** @test */
    public function user_cannot_update_another_users_workspace()
    {
        $user = User::factory()->create();
        $otherUser = User::factory()->create();

        $workspace = Workspace::factory()->create([
            'user_id' => $otherUser->id
        ]);

        $response = $this->auth($user)
            ->putJson("/api/me/workspace/{$workspace->id}", [
                'name' => 'Hacked'
            ]);

        $response->assertStatus(404);
    }

    /** @test */
    public function user_can_delete_workspace()
    {
        $user = User::factory()->create();

        $workspace = Workspace::factory()->create([
            'user_id' => $user->id
        ]);

        $response = $this->auth($user)
            ->deleteJson("/api/me/workspace/{$workspace->id}");

        $response->assertStatus(204);

        $this->assertDatabaseMissing('workspaces', [
            'id' => $workspace->id
        ]);
    }

    /** @test */
    public function user_cannot_delete_another_users_workspace()
    {
        $user = User::factory()->create();
        $otherUser = User::factory()->create();

        $workspace = Workspace::factory()->create([
            'user_id' => $otherUser->id
        ]);

        $response = $this->auth($user)
            ->deleteJson("/api/me/workspace/{$workspace->id}");

        $response->assertStatus(404);
    }

    /** @test */
    public function user_can_get_tasklists_for_workspace()
    {
        $user = User::factory()->create();

        $workspace = Workspace::factory()->create([
            'user_id' => $user->id
        ]);

        \App\Models\Tasklist::factory()->count(3)->create([
            'workspace_id' => $workspace->id,
            'user_id' => $user->id
        ]);

        $response = $this->auth($user)
            ->getJson("/api/me/workspace/{$workspace->id}/tasklists");

        $response->assertStatus(200)
            ->assertJsonCount(3);
    }

    /** @test */
    public function user_cannot_access_another_users_workspace_tasklists()
    {
        $user = User::factory()->create();
        $otherUser = User::factory()->create();

        $workspace = Workspace::factory()->create([
            'user_id' => $otherUser->id
        ]);

        $response = $this->auth($user)
            ->getJson("/api/me/workspace/{$workspace->id}/tasklists");

        $response->assertStatus(404);
    }

    /** @test */
    public function user_can_create_workspace_from_json()
    {
        $user = User::factory()->create();

        $jsonPayload = [
            "workflow" => [
                "name" => "Fishing",
                "lists" => [
                    [
                        "name" => "Prepare for Fishing",
                        "tasks" => [
                            ["description" => "Buy a fishing rod"],
                            ["description" => "Buy bait"],
                            ["description" => "Pack a lunch"],
                            ["description" => "Check weather conditions"],
                            ["description" => "Pack sunscreen"],
                            ["description" => "Pack a hat"]
                        ]
                    ],
                    [
                        "name" => "Fishing at the Lake",
                        "tasks" => [
                            ["description" => "Find a good fishing spot"],
                            ["description" => "Cast your line"],
                            ["description" => "Wait for a bite"],
                            ["description" => "Reel in the fish"],
                            ["description" => "Clean the fish"],
                            ["description" => "Prepare the fish for cooking"]
                        ]
                    ],
                    [
                        "name" => "Cooking the Fish",
                        "tasks" => [
                            ["description" => "Choose a cooking method"],
                            ["description" => "Prepare the cooking area"],
                            ["description" => "Season the fish"],
                            ["description" => "Cook the fish"],
                            ["description" => "Serve the fish"],
                            ["description" => "Clean up the cooking area"]
                        ]
                    ],
                    [
                        "name" => "Enjoying the Meal",
                        "tasks" => [
                            ["description" => "Set the table"],
                            ["description" => "Serve the fish"],
                            ["description" => "Pour drinks"],
                            ["description" => "Light candles"],
                            ["description" => "Enjoy the meal"],
                            ["description" => "Clear the table"]
                        ]
                    ],
                    [
                        "name" => "Disposing of the Remains",
                        "tasks" => [
                            ["description" => "Dispose of fish bones"],
                            ["description" => "Clean the dishes"],
                            ["description" => "Put away leftovers"],
                            ["description" => "Take out the trash"],
                            ["description" => "Wash the fishing gear"],
                            ["description" => "Store the fishing gear"]
                        ]
                    ]
                ]
            ]
        ];

        $response = $this->auth($user)
            ->postJson('/api/me/workspace/import-json', $jsonPayload);

        // Assert successful creation
        $response->assertStatus(204); // or 201 if you return a message

        // Assert workspace created
        $this->assertDatabaseHas('workspaces', [
            'name' => 'Fishing',
            'user_id' => $user->id,
        ]);

        // Assert some lists created
        $this->assertDatabaseHas('tasklists', [
            'name' => 'Prepare for Fishing',
        ]);
        $this->assertDatabaseHas('tasklists', [
            'name' => 'Fishing at the Lake',
        ]);

        // Assert some tasks created
        $this->assertDatabaseHas('tasks', [
            'description' => 'Buy a fishing rod',
        ]);
        $this->assertDatabaseHas('tasks', [
            'description' => 'Reel in the fish',
        ]);
    }
}
