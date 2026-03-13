<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('tasklists', function (Blueprint $table) {
            $table->enum('done_order', ['top', 'bottom'])->nullable();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('tasklists', function (Blueprint $table) {
            $table->dropColumn('done_order');
        });
    }
};
