<?php

use Faker\Generator as Faker;
use App\Models\User;

$factory->define(User::class, function (Faker $faker) {
    return [
        'name' => $faker->name,
        'email' => $faker->unique()->safeEmail,
        'email_verified_at' => now(),
        'password' => bcrypt('password'),
        'address' => $faker->address,
        'phone' => $faker->phoneNumber,
        'birth_date' => $faker->date(),
        'gender' => $faker->randomElement(['male', 'female']),
        'image' => 'uploads/users/default.png',
        'background_image' => 'uploads/users/bg_default.png',
        'remember_token' => \Illuminate\Support\Str::random(10),
    ];
});
