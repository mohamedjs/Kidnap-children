<?php

namespace App\Http\Controllers;

use App\Post;
use Illuminate\Http\Request;
use App\PostImage;
use Auth;
use GuzzleHttp\Client;
use GuzzleHttp\HandlerStack;
use GuzzleHttp\Middleware;
use Psr\Http\Message\RequestInterface;
class PostController extends Controller
{
    /**
     * Display a listing of the resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
        return view('front.post');
    }

    /**
     * Show the form for creating a new resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function create()
    {

    }

    /**
     * Store a newly created resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function store(Request $request)
    {
      $arr = [];
      $output = [];
      $images = $request->image;
      foreach ($images as $image) {
        $value['image'] = $image;
        array_push($arr,$value);
        if ( ! is_array( $image ) ) {
           $output[] = [
              'name'     => 'file[]',
              'contents' => fopen( $image->getPathname(), 'r' ),
              'filename' => $image->getClientOriginalName()
           ];
           continue;
        }
      }
        $post = Post::create([
            'user_id' => Auth::id() ,
            'name' => 'name' ,
            'birth_date' => '2018-9-1',
            'age' => 2,
            'type' => 'misses',
            'desc' =>$request->desc,
            'region_id' => 1 ,
            'gender' => 1 ,
            'lat' => 13.232 ,
            'lang' => 14.2332 ,
            'found' => 0
        ]);
        $client = new Client(['base_uri' => 'https://api-missed-gb.herokuapp.com/']);
        $response = $client->request('POST', '/api/detect_image',[
        'multipart' => $output]);
        //return json_decode($response);
        $id = json_decode($response->getBody()) ;
        $data = PostImage::whereIn('id',$id)->get();
        $post->images()->createMany($arr);
        count($id) > 0 ? $post->results()->attach($id):'';
        return back()->with(['data' => $data]);
    }

    /**
     * Display the specified resource.
     *
     * @param  \App\Post  $post
     * @return \Illuminate\Http\Response
     */
    public function show(Post $post)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     *
     * @param  \App\Post  $post
     * @return \Illuminate\Http\Response
     */
    public function edit(Post $post)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \App\Post  $post
     * @return \Illuminate\Http\Response
     */
    public function update(Request $request, Post $post)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     *
     * @param  \App\Post  $post
     * @return \Illuminate\Http\Response
     */
    public function destroy(Post $post)
    {
        //
    }
}
