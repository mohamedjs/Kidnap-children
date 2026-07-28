<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class AddDenderToUsers extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::table('users', function (Blueprint $table) {
            if (!Schema::hasColumn('users', 'gender')) {
                $table->string('gender')->nullable()->default('male')->after('phone');
            }
            if (!Schema::hasColumn('users', 'birth_date')) {
                $table->date('birth_date')->nullable()->after('password');
            }
            if (!Schema::hasColumn('users', 'background_image')) {
                $table->string('background_image')->nullable()->after('image');
            }
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('users', function (Blueprint $table) {
            $table->dropColumn('gender');
            $table->dropColumn('birth_date');
            $table->dropColumn('background_image');
        });
    }
}
