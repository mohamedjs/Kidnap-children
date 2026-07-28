<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateAiMatchesTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('ai_matches', function (Blueprint $table) {
            $table->increments('id');
            $table->unsignedInteger('source_post_id');
            $table->foreign('source_post_id')->references('id')->on('posts')->onDelete('cascade');
            $table->unsignedInteger('matched_post_id');
            $table->foreign('matched_post_id')->references('id')->on('posts')->onDelete('cascade');
            $table->double('confidence', 8, 2)->default(0.0);
            $table->boolean('face_detected')->default(true);
            $table->string('status')->default('matched');
            $table->text('raw_response')->nullable();
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
        Schema::dropIfExists('ai_matches');
    }
}
