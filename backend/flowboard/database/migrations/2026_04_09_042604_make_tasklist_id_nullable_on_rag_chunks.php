<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('rag_chunks', function (Blueprint $table) {
            $table->foreignId('tasklist_id')
                ->nullable()
                ->change();
        });
    }

    public function down(): void
    {
        Schema::table('rag_chunks', function (Blueprint $table) {
            $table->foreignId('tasklist_id')
                ->nullable(false)
                ->change();
        });
    }
};
