<?php

use Faker\Generator as Faker;
use App\Models\PostImage;
use App\Models\Post;

$factory->define(PostImage::class, function (Faker $faker) {
    $postImageUrls = [
        'https://images.unsplash.com/photo-1503454537688-e6876206b57a?w=800&h=600&fit=crop',
        'https://images.unsplash.com/photo-1516981080057-c72920e16d26?w=800&h=600&fit=crop',
        'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=800&h=600&fit=crop',
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop',
        'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&h=600&fit=crop',
        'https://images.unsplash.com/photo-1517457373614-b7152f800fd1?w=800&h=600&fit=crop',
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop',
        'https://images.unsplash.com/photo-1517608918720-8f6370ecbed3?w=800&h=600&fit=crop',
    ];

    return [
        "post_id" => function () {
            return Post::inRandomOrder()->first()->id ?? factory(Post::class)->create()->id;
        },
        "image" => $faker->randomElement($postImageUrls),
    ];
});
