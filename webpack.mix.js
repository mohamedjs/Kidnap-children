const mix = require('laravel-mix');

/*
 |--------------------------------------------------------------------------
 | Mix Asset Management
 |--------------------------------------------------------------------------
 |
 | Mix provides a clean, fluent API for defining some Webpack build steps
 | for your Laravel application. By default, we are compiling the Sass
 | file for the application as well as bundling up all the JS files.
 |
 */
mix.setPublicPath('./')
  .js([
  'resources/js/app.js',
  'front/js/slick.min.js',
  'front/js/selectize.js',
  'front/js/progressbar.min.js',
  'front/js/sweetalert2.min.js',
  'front/js/rangeslider.js',
  'front/js/jquery-ui.js',
  'front/js/plugin.js'
], 'front/js/app.js')
   .sass('front/scss/style.scss', 'public/front/css');
