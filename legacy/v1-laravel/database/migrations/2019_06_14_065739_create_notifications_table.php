<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateNotificationsTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('notifications', function (Blueprint $table) {
            $table->increments('id');
            $table->string('title');
            $table->text('content');
            $table->string('notification_url');
            $table->string('type')->nullable();
            $table->Integer('seen')->default(0);
            $table->unsignedInteger("send_id");
            $table->foreign('send_id')->references('id')->on('users')->onUpdate('RESTRICT')->onDelete('CASCADE');
            $table->unsignedInteger("receive_id");
            $table->foreign('receive_id')->references('id')->on('users')->onUpdate('RESTRICT')->onDelete('CASCADE');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('notifications');
    }
}
