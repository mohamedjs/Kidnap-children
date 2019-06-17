<?php

use Faker\Generator as Faker;
use App\Models\Post;
use App\Models\User;

$factory->define(Post::class, function (Faker $faker) {
    return [
        "user_id" => User::query()->inRandomOrder()->get()[0],
        "name" => $faker->name,
        "gender" => $faker->randomElement([1, 2]),
        "age" => random_int(4, 50),
        "birth_date" => \Carbon\Carbon::now()->toDateString(),
        "description" => $faker->text,
        "lat" => $faker->latitude,
        "lng" => $faker->latitude,
        "type" => $faker->randomElement(["founded", "missed"])
    ];
});
