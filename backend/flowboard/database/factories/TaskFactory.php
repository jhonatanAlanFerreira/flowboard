<?php

namespace Database\Factories;

use App\Models\User;
use App\Models\Tasklist;
use Illuminate\Database\Eloquent\Factories\Factory;

class TaskFactory extends Factory
{
    public function definition(): array
    {
        return [
            'description' => fake()->sentence(),
            'order' => fake()->numberBetween(1, 10),
            'done' => false,
            'tasklist_id' => Tasklist::factory(),
            'user_id' => User::factory(),
        ];
    }
}