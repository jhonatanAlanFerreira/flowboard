<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('rag_chunks', function (Blueprint $table) {
            $table->id();
            $table->enum('type', ['task', 'list']);

            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('workspace_id')->constrained()->cascadeOnDelete();

            $table->foreignId('tasklist_id')->constrained()->cascadeOnDelete();
            $table->foreignId('task_id')->nullable()->constrained()->cascadeOnDelete();

            $table->text('content');
            $table->text('task_description')->nullable();

            $table->json('metadata')->nullable();

            $table->boolean('has_embedding')->default(false);

            $table->timestamps();

            $table->index(['task_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('rag_chunks');
    }
};
