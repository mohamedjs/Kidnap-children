<?php

use Faker\Generator as Faker;
use App\Models\PostImage;
use App\Models\Post;

$factory->define(PostImage::class, function (Faker $faker) {
    $gender = $faker->randomElement(['men', 'women']);
    $portraitNum = random_int(1, 32);

    return [
        "post_id" => function () {
            return Post::inRandomOrder()->first()->id ?? factory(Post::class)->create()->id;
        },
        "image" => "https://randomuser.me/api/portraits/{$gender}/{$portraitNum}.jpg",
    ];
});
