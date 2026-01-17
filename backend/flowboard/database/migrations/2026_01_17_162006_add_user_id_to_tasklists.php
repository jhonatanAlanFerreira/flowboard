<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('tasklists', function (Blueprint $table) {
            $table->unsignedBigInteger('user_id');
        });

        DB::statement("
            UPDATE tasklists
            INNER JOIN workspaces ON workspaces.id = tasklists.workspace_id
            SET tasklists.user_id = workspaces.user_id
        ");

        Schema::table('tasklists', function (Blueprint $table) {
            $table->foreign('user_id')
                ->references('id')
                ->on('users')
                ->cascadeOnDelete();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('tasklists', function (Blueprint $table) {
            $table->dropForeign(['user_id']);
            $table->dropColumn('user_id');
        });
    }
};
