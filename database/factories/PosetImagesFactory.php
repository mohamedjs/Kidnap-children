<?php

use Faker\Generator as Faker;
use App\Models\PostImage;

$date_path = date("Y") . '/' . date("m") . '/' . date("d") . '/';
$path = base_path() . '/front/uploads/posts/' . $date_path;
if (!\File::exists($path)) {
    \File::makeDirectory($path, 0777, true);
}
$factory->define(PostImage::class, function (Faker $faker) use ($path,$date_path){
    return [
        "image" => url('GB/front/uploads/posts/' . $date_path).'/'.$faker->image($path,400,300, null, false),
    ];
});
