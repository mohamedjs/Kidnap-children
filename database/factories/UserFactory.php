<?php

use Faker\Generator as Faker;
use App\Models\User;

$factory->define(User::class, function (Faker $faker) {
    $gender = $faker->randomElement(['male', 'female']);
    $portraitNum = random_int(1, 32);
    $genderPath = ($gender === 'male') ? 'men' : 'women';

    return [
        'name' => $faker->name,
        'email' => $faker->unique()->safeEmail,
        'email_verified_at' => now(),
        'password' => bcrypt('password'),
        'address' => $faker->address,
        'phone' => $faker->phoneNumber,
        'birth_date' => $faker->date(),
        'gender' => $gender,
        'image' => "https://randomuser.me/api/portraits/{$genderPath}/{$portraitNum}.jpg",
        'background_image' => 'https://picsum.photos/1200/400?random=' . random_int(1, 10000),
        'remember_token' => \Illuminate\Support\Str::random(10),
    ];
});
