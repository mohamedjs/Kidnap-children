<?php

use Faker\Generator as Faker;
use App\Models\User;

$factory->define(User::class, function (Faker $faker) {
    $avatarUrls = [
        'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1510227272981-482c63d21129?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1519046904884-53103b34b206?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1507539332640-7a1e6e7ce338?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1512996750537-4e5f32fbfc2f?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1496440737103-cd596325d559?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1517849755707-55dcf41e3835?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1495954484750-af469f1357be?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1519085360771-9852cab9f991?w=400&h=400&fit=crop',
    ];

    $backgroundUrls = [
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&h=400&fit=crop',
        'https://images.unsplash.com/photo-1491466424936-e304919aada7?w=1200&h=400&fit=crop',
        'https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=1200&h=400&fit=crop',
        'https://images.unsplash.com/photo-1452587925148-ce544e77e70d?w=1200&h=400&fit=crop',
        'https://images.unsplash.com/photo-1469474969175-56ceb8ff6ffd?w=1200&h=400&fit=crop',
    ];

    return [
        'name' => $faker->name,
        'email' => $faker->unique()->safeEmail,
        'email_verified_at' => now(),
        'password' => bcrypt('password'),
        'address' => $faker->address,
        'phone' => $faker->phoneNumber,
        'birth_date' => $faker->date(),
        'gender' => $faker->randomElement(['male', 'female']),
        'image' => $faker->randomElement($avatarUrls),
        'background_image' => $faker->randomElement($backgroundUrls),
        'remember_token' => \Illuminate\Support\Str::random(10),
    ];
});
