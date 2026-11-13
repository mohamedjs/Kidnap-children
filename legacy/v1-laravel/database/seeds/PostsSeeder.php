<?php

use Illuminate\Database\Seeder;
use App\Models\Post;
use App\Models\PostImage;

class PostsSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        factory(Post::class, 10)->create()->each(function ($post) {
            $num = random_int(2, 9);

            for ($i =0; $i<$num; $i++) {
                $post->images()->save(factory(PostImage::class)->make());
            }
        });
    }
}
