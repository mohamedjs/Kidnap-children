<?php

use Illuminate\Http\Request;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| is assigned the "api" middleware group. Enjoy building your API!
|
*/

//Route::middleware('auth:api')->get('/user', function (Request $request) {
//    return $request->user();
//});
//Route::post('/test/{lat}/{lang}',function($lat,$lang){
//
//    $KAABA_LATITUDE = 21.422517;
//
//    $KAABA_LONGITUDE = 39.826166;
//
//       if (!is_numeric($lat) || !is_numeric($lang)) {
//           throw new \Exception('AlQibla::Calculation ::: Please pass a numeric value for the latitude and longitude.');
//       }
//       $A = deg2rad($KAABA_LONGITUDE - $lang);
//       $b = deg2rad(90 - $lat);
//       $c = deg2rad(90 -$KAABA_LATITUDE);
//       $C = rad2deg(atan2(sin($A), sin($b) * tan(M_PI_2 - $c) - cos($b) * cos($A)));
//       // Azimuth is not negative
//       $C += ($C < 0) * 360;
//       return $C;
//});
// function cot($arg)
//{
//    return tan(M_PI_2 - $arg);
//}

Route::prefix('/')->attribute('namespace', 'Frontend')->group(function () {
    Route::resource("posts", "PostController");
    Route::resource("comments", "CommentController");
});
