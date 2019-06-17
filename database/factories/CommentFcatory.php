<?php

use Faker\Generator as Faker;
use App\Models\User;
use App\Models\Post;
use App\Models\Comment;

$factory->define(Comment::class, function (Faker $faker) {
    return [
        "user_id" => User::query()->inRandomOrder()->get()[0],
        "post_id" => Post::query()->inRandomOrder()->get()[0],
        "comment" => $faker->text(random_int(20, 50))
    ];
});
