<?php

use Faker\Generator as Faker;
use App\Models\PostImage;
use App\Models\Post;

$factory->define(PostImage::class, function (Faker $faker) {
    return [
        "post_id" => function () {
            return Post::inRandomOrder()->first()->id ?? factory(Post::class)->create()->id;
        },
        "image" => "uploads/posts/sample.jpg",
    ];
});
