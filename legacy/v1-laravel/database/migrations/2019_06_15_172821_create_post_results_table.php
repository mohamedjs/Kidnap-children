<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreatePostResultsTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('post_results', function (Blueprint $table) {
            $table->increments('id');
            $table->integer('post_id')->unsigned();
            $table->foreign("post_id")->references('id')->on('posts')->onDelete('cascade')->onUpdate('cascade') ;
            $table->integer('result_id')->unsigned();
            $table->foreign("result_id")->references('id')->on('posts')->onDelete('cascade')->onUpdate('cascade') ;
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
        Schema::dropIfExists('post_results');
    }
}
