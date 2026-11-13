<?php

use Faker\Generator as Faker;
use App\Models\Post;
use App\Models\User;

$factory->define(Post::class, function (Faker $faker) {
    return [
        "user_id" => function () {
            return User::inRandomOrder()->first()->id ?? factory(User::class)->create()->id;
        },
        "name" => $faker->name,
        "gender" => $faker->randomElement(["male", "female"]),
        "age" => random_int(1, 17),
        "birth_date" => $faker->date(),
        "description" => $faker->paragraph,
        "lat" => (string)$faker->latitude,
        "lng" => (string)$faker->longitude,
        "type" => $faker->randomElement(["founded", "missed"])
    ];
});
