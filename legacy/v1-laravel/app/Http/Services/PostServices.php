<?php
/**
 * Created by PhpStorm.
 * User: ghost
 * Date: 6/1/19
 * Time: 12:58 AM
 */

namespace App\Http\Services;

use App\Models\Post;
use App\Models\PostImage;
use Illuminate\Http\Request;

class PostServices
{
    /**
     * @var UploaderService
     */
    private $uploaderService;


    /**
     * PostServices constructor.
     */
    public function __construct(UploaderService $uploaderService)
    {
        $this->uploaderService = $uploaderService;
    }

    public function fillPostFromRequest(Request $request, Post $post = null)
    {
        if (!$post) {
            $post = new Post();
        }

        $post->fill($request->all());
        $post->save();

        if ($request->has("images")) {
            $this->savePostImages($request->file("images"), $post);
        }

        return $post;
    }

    private function savePostImages($images, Post $post)
    {
        $postImages = [] ;
        foreach ($images as $image) {
            $img = $this->uploaderService->upload($image, "posts") ;
            $postImages[] = new PostImage(['image' => $img]);
        }

        $post->images()->saveMany($postImages) ;
    }
}
