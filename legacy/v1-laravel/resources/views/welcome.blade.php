<!doctype html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <title>Laravel</title>

        <!-- Fonts -->
        <link href="https://fonts.googleapis.com/css?family=Nunito:200,600" rel="stylesheet" type="text/css">

        <!-- Styles -->
        <style>
            html, body {
                background-color: #fff;
                color: #636b6f;
                font-family: 'Nunito', sans-serif;
                font-weight: 200;
                height: 100vh;
                margin: 0;
            }

            .full-height {
                height: 100vh;
            }

            .flex-center {
                align-items: center;
                display: flex;
                justify-content: center;
            }

            .position-ref {
                position: relative;
            }

            .top-right {
                position: absolute;
                right: 10px;
                top: 18px;
            }

            .content {
                text-align: center;
            }

            .title {
                font-size: 84px;
            }

            .links > a {
                color: #636b6f;
                padding: 0 25px;
                font-size: 13px;
                font-weight: 600;
                letter-spacing: .1rem;
                text-decoration: none;
                text-transform: uppercase;
            }

            .m-b-md {
                margin-bottom: 30px;
            }
        </style>
        <script>
       var zoom = 20; // 18 for mobile phones because the geolocation is more accurate

       function init() {
         // Don't bother if the web browser doesn't support cross-document messaging
         if (window.postMessage) {
           if (navigator && navigator.geolocation) {
             try {
               navigator.geolocation.getCurrentPosition(function(pPos) {
               send(pPos.coords.latitude, pPos.coords.longitude);
             }, function() {});
             } catch (e) {}
           } else if (google && google.gears) {
             // Relevant if targeting mobile phones (some of which may have Google Gears)
             try {
               var geoloc = google.gears.factory.create("beta.geolocation");
               geoloc.getCurrentPosition(function(pPos) {
               send(pPos.latitude, pPos.longitude);
             }, function() {});
             } catch (e) {}
           }
         }
       }

       function send(pLat, pLng) {
         var myiframe = document.getElementById("myiframe").contentWindow;
         // The third parameter, zoom, is optional
         myiframe.postMessage(pLat + "," + pLng + "," + zoom, "http://qib.la");
       }

       window.onload=init;
      </script>
    </head>
    <body>
        <div class="flex-center position-ref full-height">
            @if (Route::has('login'))
                <div class="top-right links">
                    @auth
                        <a href="{{ url('/home') }}">Home</a>
                    @else
                        <a href="{{ route('login') }}">Login</a>

                        @if (Route::has('register'))
                            <a href="{{ route('register') }}">Register</a>
                        @endif
                    @endauth
                </div>
            @endif

            <div class="content">
                <div class="title m-b-md">
                    Laravel
                </div>

                <div class="links">
                    <a href="https://laravel.com/docs">Documentation</a>
                    <a href="https://laracasts.com">Laracasts</a>
                    <a href="https://laravel-news.com">News</a>
                    <a href="https://nova.laravel.com">Nova</a>
                    <a href="https://forge.laravel.com">Forge</a>
                    <a href="https://github.com/laravel/laravel">GitHub</a>
                </div>
            </div>
        </div>
          <iframe id="myiframe" src="http://qib.la/embed/" width="400" height="400">
          Check the prayer direction towards the Ka'ba in Makkah at
          <a href="http://qib.la/">Qibla Direction</a>.
        </iframe>
        <button type="button" id="click" name="button">click</button>
        <script src="https://ajax.aspnetcdn.com/ajax/jQuery/jquery-3.3.1.min.js"></script>
        <script type="text/javascript">
        $('#click').click(function(){
          if (navigator.geolocation)
          {
            navigator.geolocation.getCurrentPosition(showPosition);
          }
          function showPosition(position)
          {
            $.post('api/test/'+position.coords.latitude+'/'+position.coords.longitude,function(response){
              console.log(response > 0 ? response+'degrees East of North' : response+'degrees West of North');
            })
          }
        })

        </script>
    </body>
</html>
