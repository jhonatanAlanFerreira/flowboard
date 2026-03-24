<?php

namespace Database\Factories;

use App\Models\User;
use App\Models\Workspace;
use Illuminate\Database\Eloquent\Factories\Factory;

class TasklistFactory extends Factory
{
    public function definition(): array
    {
        return [
            'name' => fake()->word(),
            'order' => fake()->numberBetween(1, 10),
            'workspace_id' => Workspace::factory(),
            'user_id' => User::factory(),
            'done_order' => "top",
        ];
    }
}