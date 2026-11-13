<?php

use Faker\Generator as Faker;
use App\Models\User;
use App\Models\Post;
use App\Models\Comment;

$factory->define(Comment::class, function (Faker $faker) {
    return [
        "user_id" => function () {
            return User::inRandomOrder()->first()->id ?? factory(User::class)->create()->id;
        },
        "post_id" => function () {
            return Post::inRandomOrder()->first()->id ?? factory(Post::class)->create()->id;
        },
        "comment" => $faker->sentence
    ];
});
