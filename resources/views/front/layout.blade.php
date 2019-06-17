<!DOCTYPE html>
<html>
    <head>
      <title>Ecovve</title>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
      <!-- CSRF Token -->
      <meta name="csrf-token" content="{{ csrf_token() }}">
      <meta name="base_url" content="{{ url('/')}}">
      <meta name="window.default_locale" content="{{ App::getLocale()}}">
      <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.4.1/css/all.css" integrity="sha384-5sAR7xN1Nv6T6+dT2mhtzEpVJvfS3NScPQTrOxhwjIuvcA67KV2R5Jz6kr4abQsz" crossorigin="anonymous">
      <!-- common link-->
      <link rel="stylesheet" href="{{url('front/css/rangeslider.css')}}">
      <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Poppins:400,500,600,700,800,900">
      <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Tajawal:400,500,700,800">
      <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Nunito:400,500,700,800,900">
      <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Great+Vibes">
      <link rel="stylesheet" href="{{url('front/css/slick.min.css')}}">
      <link rel="stylesheet" href="{{url('front/css/perfect-scrollbar.css')}}">
      <link rel="stylesheet" href="https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
      <link rel="stylesheet" href="{{url('front/css/swiper.min.css')}}">
      <link rel="stylesheet" href="{{url('front/css/selectize.css')}}">
      <link rel="stylesheet" href="{{url('front/css/bootstrap.min.css')}}">
      <link rel="stylesheet" href="{{url('front/css/themes/bootstrap-v3.css')}}">
      <link rel="stylesheet" href="{{url('front/css/bootstrap-datetimepicker.min.css')}}">
      <link rel="stylesheet" href="{{url('front/css/animate.css')}}">
      <link rel="stylesheet" href="{{url('front/css/noty.css')}}">
      <link rel="stylesheet" href="{{url('front/css/style.css')}}">
      <title>Missed | @yield('page_title')</title>
      <style media="screen">
      .dashboard-profile>.dashboard-profile-content>.cover-box .profile-info{
      background: url("{{ Auth::user()->background_image }}") no-repeat center center
      }
          .dashboard-header.justify-content-between
          {
            position: fixed;width: 82%;z-index: 99;
          }
          @media only screen and (max-width: 768px) {
        .photo-box-slider{
          width:100% !important;
        }
        .post-data{
          width: 100% !important;
        }
        .dashboard-header.justify-content-between{
          position: fixed;width: 100%;z-index: 99;
        }
      }
          #loading {
            /* height: 40px;
            position: absolute; */
            left: calc(50% - 40px);
            top: calc(50% - 10px);
            text-align: center;
            -webkit-touch-callout: none;
            -webkit-user-select: none;
            -khtml-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
          }
          #loading span {
            width: 10px;
            height: 10px;
            margin: 2px;
            background: #f50;
            border-radius: 50%;
            display: inline-block;
            transition: all 2s ease;
            animation: wave 2.5s ease infinite;
          }
          #loading span:nth-child(2) {
            background: #ff2;
            animation-delay: 100ms;

          }
          #loading span:nth-child(3) {
            background: #2f2;
            animation-delay: 200ms;
          }
          @keyframes wave {
            0%, 100% {
              transform: translate(0, 0);

            }
            40% {
              transform: translate(0, 20px);
              opacity: 0;
            }
            10% {
              transform: translate(0, -20px);
            }
          }
          .image_item{
            margin-bottom: 3px;
            border-radius: 6px;
          }
          #dynamic{
            border-radius: 6px;
          }
          .loading_data {
              text-align: center;
              color: #000;
              z-index: 9;
              padding: 8px 18px;
              border-radius: 5px;
              left: calc(50% - 45px);
              top: calc(50% - 18px);
            }

            .fade-enter-active, .fade-leave-active {
              transition: opacity 0.5s;
            }

            .fade-enter, .fade-leave-to {
              opacity: 0;
            }
          #app{
            padding-top: 5%;
          }
      </style>
      <!--if lt IE 9 script(src='http://cdnjs.cloudflare.com/ajax/libs/es5-shim/2.0.8/es5-shim.min.js')-->
    </head>
  <body>
    <main class="customer-dashboard">
      <div class="customer-dashboard-asidemenu">
        <div class="close-customer-dashboard-aside"></div>
        <div class="menu-header d-flex justify-content-between align-items-center">
          <div class="logo-box"><img class="img-fluid" src="{{url('front/images/logo.png')}}"></div><a class="menu-box-btn customer-dashboard-asidemenu-colapse-btn" href="#"><span></span></a><a class="toggle-customer-dashboard-header" href="#"><i class="fas fa-ellipsis-v"></i></a><a class="menu-box-btn customer-dashboard-asidemenu-mobile-btn" href="#"><span></span></a>
        </div>
        <div class="menu-body perfect-scroll">
          <div class="customer-box"><a class="customer-photo" href="#"><img class="img-fluid" src="{{Auth::user()->image}}"></a>
            <h3 class="customer-name mb-3"><a href="#">{{Auth::user()->name}}</a></h3>
            <ul class="customer-tools list-unstyled">
              <li id="notifiy-count"><a class="customer-tool-item" href="{{ url('all_notification') }}"><i class="fas fa-bell"></i>
                  <div class="noitfy"><span><?php echo \App\Models\Notification::where('receive_id',Auth::id())->where('seen',0)->count() ?></span></div></a></li>
              <li><a class="customer-tool-item" href="{{ url('chatroom') }}"><i class="fab fa-facebook-messenger"></i>
                  <div class="noitfy"><span>9</span></div></a></li>
            </ul>
          </div>
          <ul class="list-unstyled customer-menu perfect-scroll">
            <li><a class="customer-menu-item" href="{{ url('/') }}"><i class="fas fa-home"></i><span>HOME</span></a></li>
            <li><a class="customer-menu-item" href="{{ url('profile') }}"><i class="fas fa-user"></i><span>PROFILE</span></a></li>
            <li><a class="customer-menu-item" href="{{ url('/missedperson') }}"><i class="fas fa-search"></i><span>LOOK FOR PERSON</span></a></li>
            <li><a class="customer-menu-item" href="{{ url('/foundperson') }}"><i class="far fa-address-card"></i><span>FOUND PERSON</span></a></li>
            @if(Auth::user())
            <li><a class="customer-menu-item" href="{{ route('logout') }}"
                 onclick="event.preventDefault();
                               document.getElementById('logout-form').submit();"><i class="fas fa-sign-out-alt"></i><span>LOGOUT</span></a>
                 <form id="logout-form" action="{{ route('logout') }}" method="POST" style="display: none;">
                     @csrf
                 </form>
            </li>
            @endif
          </ul>
        </div>
      </div>
      <div class="customer-dashboard-content dashboard-friends dashboard-profile">
        <div class="dashboard-header d-flex justify-content-between">
          <h2 class="title"><i class="fas fa-home"></i><span>HOME</span></h2>
          <div class="lang-notify d-flex justify-content-start">
            <div id="notification-vue">
              <div class="customer-notification-dropdown"><a class="alarm-box" href="#" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" id="notification-show"><img class="img-fluid" src="{{url('front/images/alarm.png')}}">
                <div class="circle"><span>@{{ notification_count }}</span></div></a>
              <div class="dropdown-menu bg-fff round-20" id="notifications-list-dropdown" aria-labelledby="notification-show">
                <h3 class="notifications-list-title">Notifications<a class="close" href="#" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i class="fa fa-times"></i></a></h3>
                <div class="stipped-rows perfect-scroll">
                  <ul class="list-unstyled mb-0">
                    <li v-if="notifications.length>0" v-for="notification in notifications">
                      <a class="notification-row" :href="notification.notification_url">
                        <div class="round-10 img"><img class="img-fluid" :src="notification.sender.name"></div>
                        <div class="info">
                          <h3 class="brand">@{{notification.sender.name}}</h3>
                          <div class="subline"><span class="time">@{{ moment(notification.created_at).fromNow() }}</span><span class="title">@{{notification.title}}</span></div>
                        </div>
                       </a>
                      </li>
                  </ul>
                </div>
                <div class="notifications-footer"><a href="{{ url('all_notification') }}">View All</a></div>
              </div>
            </div>
            </div>
          </div>
        </div>
        @yield('content')
      </div>
    </main>
    <div class="add-to-group-modal modal fade" id="add-to-group" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <form>
              <div class="search-group">
                <div class="icon-box"><i class="fas fa-search"></i></div>
                <input type="text" placeholder="Search for a group">
              </div>
            </form>
            <button class="close" type="button" data-dismiss="modal" aria-label="Close"><img class="img-fluid" src="images/icons/close.svg"></button>
          </div>
          <div class="modal-body">
            <ul class="friends-list list-unstyled mb-0">
              <li>
                <div class="cafe-info">
                  <div class="photo-box"><img class="img-fluid" src="{{url('front/images/cart/1.png')}}"></div>
                  <p class="friend-name">Caffee Lovers</p>
                </div><a class="add-btn" href="#">Add</a>
              </li>
              <li>
                <div class="cafe-info">
                  <div class="photo-box"><img class="img-fluid" src="{{url('front/images/cart/2.png')}}"></div>
                  <p class="friend-name">Caffee Lovers</p>
                </div><a class="add-btn" href="#">Add</a>
              </li>
              <li>
                <div class="cafe-info">
                  <div class="photo-box"><img class="img-fluid" src="{{url('front/images/cart/1.png')}}"></div>
                  <p class="friend-name">Caffee Lovers</p>
                </div><a class="add-btn" href="#">Add</a>
              </li>
              <li>
                <div class="cafe-info">
                  <div class="photo-box"><img class="img-fluid" src="{{url('front/images/cart/2.png')}}"></div>
                  <p class="friend-name">Caffee Lovers</p>
                </div><a class="add-btn" href="#">Add</a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- script tags-->
    <script async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAndFqevHboVWDN156vJqXk1Y1-D7QR7BE&callback=initMap"></script>
    <script src="{{url('front/js/app.js')}}"></script>
    <script src="{{url('front/js/bootstrap-datetimepicker.min.js')}}"></script>
    <script src="{{url('front/js/noty.min.js')}}"></script>
    <script type="text/javascript">
        var url = window.location.href
        index_url = '{{url("/")}}'+'/';
        if(url !=  index_url)
          {
            $('.customer-menu li a').each(function () {
                if (this.href.includes(url)) {
                  $(this).addClass('active-item');
                }
            });
          }
          else
          {
            $('.customer-menu li a:first').addClass('active-item')
          }
    </script>
    <script>
      const app = new Vue({
      el:'#notification-vue',
      data:{
        notifications:[],
        notification_count:0,
        uri : base_url
      },
      methods:{
        get_notification(){
          var _this = this
          axios.get(this.uri+'/get_notification').then(function (response) {
            _this.notifications = response.data.notifications;
            _this.notification_count = response.data.unread_notify;
          }).catch(
            error => console.log(error)
          );
        }
      },
      created(){
        let _this = this
        Echo.private('notification.'+{{ Auth::id() }})
          .listen('.notification.created', (e) => {
            _this.get_notification()
            _this.notification_count = _this.notification_count+1
            $('#notifiy-count .noitfy').html('<span>'+_this.notification_count+'</span>')
            new Noty({
                  type: 'success',
                  theme: 'bootstrap-v3',
                  layout: 'bottomRight',
                  closeWith: ['click', 'button'],
                  buttons     : false,
                  progressBar : true,
                  text: e.message,
                  animation: {
                     open: 'animated bounceInRight', // Animate.css class names
                     close: 'animated bounceOutRight' // Animate.css class names
                 },
                 sound:{
                   source:['{{ asset('front/svg/nice-cut.wav') }}'],
                   volume : 1,
                   conditions: ['docVisible', 'docHidden']
                 }
                }).show();
          })
        _this.get_notification()
      }
    });
    </script>

  </body>
</html>
