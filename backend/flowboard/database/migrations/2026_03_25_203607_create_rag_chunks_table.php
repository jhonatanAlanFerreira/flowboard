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

            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('workspace_id')->constrained()->cascadeOnDelete();

            $table->foreignId('tasklist_id')->nullable()->constrained()->nullOnDelete();
            $table->foreignId('task_id')->nullable()->constrained()->nullOnDelete();

            $table->string('type');

            $table->text('content');

            $table->json('metadata')->nullable();

            $table->boolean('is_durty')->default(false);

            $table->boolean('has_embedding')->default(false);

            $table->timestamps();

            $table->index(['workspace_id', 'is_durty']);
            $table->index(['workspace_id', 'type']);
            $table->index(['tasklist_id', 'type']);
            $table->index(['task_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('rag_chunks');
    }
};
