<?php

namespace Database\Factories;

use App\Models\User;
use App\Models\Workspace;
use Illuminate\Database\Eloquent\Factories\Factory;

class AiJobFactory extends Factory
{
    public function definition(): array
    {
        return [
            'user_id' => User::factory(),
            'workspace_id' => Workspace::factory(),
            'status' => fake()->randomElement(['pending', 'completed', 'failed']),
            'prompt' => fake()->sentence(),
        ];
    }
}