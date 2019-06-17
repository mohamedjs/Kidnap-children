<?php

use Faker\Generator as Faker;
use App\Models\User;

/*
|--------------------------------------------------------------------------
| Model Factories
|--------------------------------------------------------------------------
|
| This directory should contain each of the model factory definitions for
| your application. Factories provide a convenient way to generate new
| model instances for testing / seeding your application's database.
|
*/
$date_path = date("Y") . '/' . date("m") . '/' . date("d") . '/';
$path = base_path() . '/front/uploads/users/' . $date_path;
if (!\File::exists($path)) {
    \File::makeDirectory($path, 0777, true);
}
$factory->define(User::class, function (Faker $faker) use ($path,$date_path){
    return [
        'name' => $faker->name,
        'email' => $faker->unique()->safeEmail,
        'email_verified_at' => now(),
        'password' => '$2y$10$TKh8H1.PfQx37YgCzwiKb.KjNyWgaHb9cbcoQgdIVFlYg7B77UdFm', // secret
        "phone" => $faker->phoneNumber,
        "birth_date" => \Carbon\Carbon::now()->toDateString(),
        "gender" => $faker->randomElement(["male", "female"]),
        "image" => url('GB/front/uploads/users/' . $date_path).'/'.$faker->image($path,400,300, null, false),
        'remember_token' => str_random(10),
    ];
});
