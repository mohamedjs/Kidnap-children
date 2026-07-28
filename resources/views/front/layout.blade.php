<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
  <head>
    <title>Kidnap Children – Social Platform | @yield('page_title', 'Home')</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="A community-powered platform to help locate and report missing children using AI-assisted matching.">
    <!-- CSRF Token -->
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <meta name="base_url"   content="{{ url('/') }}">
    <meta name="window.default_locale" content="{{ App::getLocale() }}">

    <!-- Inter Font -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.4.1/css/all.css" integrity="sha384-5sAR7xN1Nv6T6+dT2mhtzEpVJvfS3NScPQTrOxhwjIuvcA67KV2R5Jz6kr4abQsz" crossorigin="anonymous">

    <!-- Vendor CSS -->
    <link rel="stylesheet" href="{{ url('front/css/rangeslider.css') }}">
    <link rel="stylesheet" href="{{ url('front/css/slick.min.css') }}">
    <link rel="stylesheet" href="{{ url('front/css/perfect-scrollbar.css') }}">
    <link rel="stylesheet" href="{{ url('front/css/swiper.min.css') }}">
    <link rel="stylesheet" href="{{ url('front/css/selectize.css') }}">
    <link rel="stylesheet" href="{{ url('front/css/bootstrap.min.css') }}">
    <link rel="stylesheet" href="{{ url('front/css/animate.css') }}">
    <link rel="stylesheet" href="{{ url('front/css/noty.css') }}">

    <!-- App CSS (compiled SCSS, includes design system) -->
    <link rel="stylesheet" href="{{ url('front/css/style.css') }}">

    <!-- Inline overrides for profile background image (user-specific) -->
    <style>
      @if(Auth::check() && Auth::user()->background_image)
      .profile-cover-img {
        background-image: url("{{ Auth::user()->background_image }}");
      }
      @endif

      /* V-cloak loader */
      [v-cloak] > * { display: none; }
      [v-cloak]::before {
        content: '';
        position: fixed;
        inset: 0;
        background: #F8FAFC;
        z-index: 9999;
      }

      /* Fade transition */
      .fade-enter-active, .fade-leave-active { transition: opacity 0.4s; }
      .fade-enter, .fade-leave-to { opacity: 0; }
    </style>
  </head>
  <body>

    <!-- ================================================================
         TOP NAVIGATION BAR
         ================================================================ -->
    <header class="topbar" role="banner">
      <!-- Logo -->
      <a class="topbar-logo" href="{{ url('/') }}" aria-label="Kidnap Children – Go to Home">
        <img src="{{ url('front/images/logo.png') }}" alt="Platform Logo">
        <span class="topbar-logo-text">Missing<span>Kids</span></span>
      </a>

      <!-- Global search -->
      <div class="topbar-search" role="search">
        <i class="fas fa-search search-icon" aria-hidden="true"></i>
        <input
          type="search"
          placeholder="Search cases, locations, names..."
          aria-label="Search missing children cases"
          id="global-search-input"
        >
      </div>

      <!-- Actions -->
      <div class="topbar-actions">
        <!-- Notifications -->
        <div id="notification-vue" style="display:flex;align-items:center;">
          <div class="customer-notification-dropdown">
            <button class="topbar-icon-btn" id="notification-show"
              data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"
              aria-label="Notifications (@{{ notification_count }} unread)">
              <i class="fas fa-bell" aria-hidden="true"></i>
              <span class="badge-count" v-if="notification_count > 0">@{{ notification_count }}</span>
            </button>
            <div class="dropdown-menu dropdown-menu-right bg-fff round-20" id="notifications-list-dropdown"
              aria-labelledby="notification-show" style="min-width:320px; margin-top:8px; border-radius:16px; box-shadow:0 20px 48px rgba(15,23,42,.16); border:1px solid #E2E8F0; padding:0; overflow:hidden;">
              <div style="padding:14px 18px; border-bottom:1px solid #E2E8F0; font-size:.875rem; font-weight:700; color:#0F172A; display:flex; justify-content:space-between; align-items:center;">
                <span>Notifications</span>
                <button class="close" data-toggle="dropdown" style="background:none;border:none;cursor:pointer;font-size:16px;color:#94A3B8;" aria-label="Close notifications">
                  <i class="fa fa-times" aria-hidden="true"></i>
                </button>
              </div>
              <div class="stipped-rows perfect-scroll" style="max-height:340px; overflow:auto;">
                <ul class="list-unstyled mb-0">
                  <li v-if="notifications.length === 0" style="padding:24px 18px; text-align:center; color:#94A3B8; font-size:.875rem;">
                    No notifications yet
                  </li>
                  <li v-for="notification in notifications" :key="notification.id" style="border-bottom:1px solid #F1F5F9;">
                    <a class="notification-row" :href="notification.notification_url"
                      style="display:flex;align-items:center;gap:12px;padding:12px 18px;transition:background .15s;"
                      onmouseover="this.style.background='#F8FAFC'" onmouseout="this.style.background=''">
                      <div style="width:36px;height:36px;border-radius:50%;background:#EFF6FF;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                        <i class="fas fa-bell" style="color:#2563EB;font-size:14px;"></i>
                      </div>
                      <div style="flex:1;min-width:0;">
                        <p style="font-size:.8125rem;font-weight:600;color:#0F172A;margin:0 0 2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">@{{ notification.sender.name }}</p>
                        <p style="font-size:.75rem;color:#64748B;margin:0;">@{{ notification.title }}</p>
                        <p style="font-size:.7rem;color:#94A3B8;margin:0;">@{{ moment(notification.created_at).fromNow() }}</p>
                      </div>
                    </a>
                  </li>
                </ul>
              </div>
              <div style="padding:10px 18px; border-top:1px solid #E2E8F0; text-align:center;">
                <a href="{{ url('all_notification') }}" style="font-size:.8125rem; font-weight:600; color:#2563EB;">View All Notifications</a>
              </div>
            </div>
          </div>
        </div>

        <!-- Messages -->
        <a href="{{ url('chatroom') }}" class="topbar-icon-btn" aria-label="Messages">
          <i class="fab fa-facebook-messenger" aria-hidden="true"></i>
        </a>

        <!-- Profile avatar -->
        <a href="{{ url('profile') }}" aria-label="View your profile">
          <img
            src="{{ Auth::user()->image }}"
            alt="{{ Auth::user()->name }} – Profile"
            class="topbar-avatar"
          >
        </a>
      </div>
    </header>
    <!-- /topbar -->

    <!-- ================================================================
         APP SHELL (three-column grid)
         ================================================================ -->
    <div class="app-shell">

      <!-- ---- LEFT SIDEBAR ------------------------------------------- -->
      <nav class="left-sidebar" aria-label="Main navigation">
        <!-- Current user mini-card -->
        <a class="sidebar-user" href="{{ url('profile') }}" aria-label="Your profile">
          <img src="{{ Auth::user()->image }}" alt="{{ Auth::user()->name }}" class="sidebar-user-avatar">
          <div class="sidebar-user-info">
            <p class="sidebar-user-name">{{ Auth::user()->name }}</p>
            <p class="sidebar-user-handle">Community Member</p>
          </div>
        </a>

        <!-- Main nav -->
        <p class="sidebar-section-label">Menu</p>

        <a class="sidebar-nav-item @if(Request::is('/') || Request::is('home')) active @endif"
           href="{{ url('/') }}" aria-current="@if(Request::is('/') || Request::is('home')) page @endif">
          <i class="fas fa-home nav-icon" aria-hidden="true"></i>
          <span>Home</span>
        </a>

        <a class="sidebar-nav-item @if(Request::is('missedperson*')) active @endif"
           href="{{ url('/missedperson') }}">
          <i class="fas fa-search nav-icon" aria-hidden="true"></i>
          <span>Missing Children</span>
          <span class="nav-badge" aria-label="Active cases">
            <?php echo \App\Models\Post::where('type','missed')->count(); ?>
          </span>
        </a>

        <a class="sidebar-nav-item @if(Request::is('foundperson*')) active @endif"
           href="{{ url('/foundperson') }}">
          <i class="far fa-address-card nav-icon" aria-hidden="true"></i>
          <span>Found Reports</span>
        </a>

        <a class="sidebar-nav-item" href="{{ url('/') }}">
          <i class="fas fa-robot nav-icon" aria-hidden="true"></i>
          <span>AI Search</span>
        </a>

        <a class="sidebar-nav-item" href="{{ url('/') }}">
          <i class="fas fa-map-marked-alt nav-icon" aria-hidden="true"></i>
          <span>Map View</span>
        </a>

        <a class="sidebar-nav-item" href="{{ url('/') }}">
          <i class="fas fa-users nav-icon" aria-hidden="true"></i>
          <span>Community</span>
        </a>

        <div class="sidebar-divider"></div>

        <p class="sidebar-section-label">Personal</p>

        <a class="sidebar-nav-item @if(Request::is('profile*')) active @endif"
           href="{{ url('profile') }}">
          <i class="fas fa-user nav-icon" aria-hidden="true"></i>
          <span>My Profile</span>
        </a>

        <a class="sidebar-nav-item @if(Request::is('all_notification*')) active @endif"
           href="{{ url('all_notification') }}">
          <i class="fas fa-bell nav-icon" aria-hidden="true"></i>
          <span>Notifications</span>
          <span class="nav-badge" id="sidebar-notif-count">
            <?php echo \App\Models\Notification::where('receive_id', Auth::id())->where('seen', 0)->count(); ?>
          </span>
        </a>

        <a class="sidebar-nav-item" href="{{ url('chatroom') }}">
          <i class="fas fa-comments nav-icon" aria-hidden="true"></i>
          <span>Messages</span>
        </a>

        <div class="sidebar-divider"></div>

        @if(Auth::user())
        <a class="sidebar-nav-item" href="{{ route('logout') }}"
           onclick="event.preventDefault(); document.getElementById('logout-form').submit();"
           style="color:#DC2626;"
           aria-label="Sign out">
          <i class="fas fa-sign-out-alt nav-icon" style="color:#DC2626;" aria-hidden="true"></i>
          <span>Logout</span>
        </a>
        <form id="logout-form" action="{{ route('logout') }}" method="POST" style="display:none;">
          @csrf
        </form>
        @endif
      </nav>
      <!-- /left-sidebar -->

      <!-- ---- CENTER CONTENT ----------------------------------------- -->
      <main class="customer-dashboard-content" id="main-content" aria-label="Main content">
        @yield('content')
      </main>
      <!-- /center -->

      <!-- ---- RIGHT SIDEBAR ------------------------------------------ -->
      <aside class="right-sidebar" aria-label="Additional information">

        <!-- Recent Missing Cases -->
        <div class="sidebar-widget">
          <div class="widget-header">
            <h2 class="widget-title"><i class="fas fa-clock" aria-hidden="true"></i> Recent Cases</h2>
            <a href="{{ url('/missedperson') }}" class="widget-link">See all</a>
          </div>
          <ul class="widget-list" aria-label="Recent missing children cases">
            @php
              $recentCases = \App\Models\Post::where('type','missed')->latest()->take(4)->get();
            @endphp
            @forelse($recentCases as $case)
            <li class="widget-list-item">
              <div class="widget-item-thumb" aria-hidden="true">
                @if($case->images->first())
                  <img src="{{ $case->images->first()->image }}" alt="" style="width:40px;height:40px;object-fit:cover;border-radius:6px;">
                @else
                  <i class="fas fa-child"></i>
                @endif
              </div>
              <div class="widget-item-info">
                <p class="item-name">{{ $case->name }}</p>
                <p class="item-sub">Age {{ $case->age }} · {{ $case->created_at->diffForHumans() }}</p>
              </div>
              <span class="item-status-dot dot-missing" title="Missing" aria-label="Status: Missing"></span>
            </li>
            @empty
            <li style="padding:16px; text-align:center; color:#94A3B8; font-size:.875rem;">No recent cases</li>
            @endforelse
          </ul>
        </div>

        <!-- AI Recommendations -->
        <div class="sidebar-widget">
          <div class="widget-header">
            <h2 class="widget-title"><i class="fas fa-robot" aria-hidden="true"></i> AI Insights</h2>
          </div>
          <div style="padding:16px;">
            <div style="background:linear-gradient(135deg,#EEF2FF,#E0E7FF);border:1px solid #C7D2FE;border-radius:10px;padding:14px;">
              <p style="font-size:.8125rem;font-weight:700;color:#4338CA;margin:0 0 6px;display:flex;align-items:center;gap:6px;">
                <i class="fas fa-brain" aria-hidden="true"></i> Smart Matching Active
              </p>
              <p style="font-size:.75rem;color:#6366F1;margin:0;line-height:1.5;">
                AI is analyzing uploaded photos against {{ \App\Models\Post::count() }} active cases.
              </p>
            </div>
          </div>
        </div>

        <!-- Emergency Contacts -->
        <div class="sidebar-widget">
          <div class="widget-header">
            <h2 class="widget-title"><i class="fas fa-phone-alt" aria-hidden="true"></i> Emergency Contacts</h2>
          </div>
          <div class="emergency-contacts">
            <div class="emergency-item">
              <i class="fas fa-phone" aria-hidden="true"></i>
              <div class="emergency-info">
                <p class="emergency-name">National Emergency</p>
                <p class="emergency-num">123</p>
              </div>
            </div>
            <div class="emergency-item">
              <i class="fas fa-child" aria-hidden="true"></i>
              <div class="emergency-info">
                <p class="emergency-name">Child Help Line</p>
                <p class="emergency-num">16000</p>
              </div>
            </div>
            <div class="emergency-item">
              <i class="fas fa-shield-alt" aria-hidden="true"></i>
              <div class="emergency-info">
                <p class="emergency-name">Police Hotline</p>
                <p class="emergency-num">122</p>
              </div>
            </div>
          </div>
        </div>

      </aside>
      <!-- /right-sidebar -->

    </div>
    <!-- /app-shell -->

    <!-- Floating Create Report Button -->
    <a href="#create-report-modal" class="fab-create-report" role="button"
       data-toggle="collapse" data-target="#create-post-body" aria-expanded="false"
       aria-label="Create a new missing child report">
      <i class="fas fa-plus" aria-hidden="true"></i>
      <span class="fab-label">Create Report</span>
    </a>

    <!-- Add to Group Modal (retained) -->
    <div class="add-to-group-modal modal fade" id="add-to-group" tabindex="-1" role="dialog"
         aria-labelledby="add-to-group-title" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="add-to-group-title">Search Groups</h5>
            <form style="flex:1;margin:0 16px;">
              <div style="position:relative;">
                <i class="fas fa-search" style="position:absolute;left:12px;top:50%;transform:translateY(-50%);color:#94A3B8;font-size:13px;" aria-hidden="true"></i>
                <input type="search" placeholder="Search for a group" style="width:100%;border:1px solid #E2E8F0;border-radius:999px;padding:8px 12px 8px 34px;font-size:.875rem;" aria-label="Search groups">
              </div>
            </form>
            <button class="close" type="button" data-dismiss="modal" aria-label="Close modal">
              <i class="fas fa-times" aria-hidden="true"></i>
            </button>
          </div>
          <div class="modal-body">
            <ul class="friends-list list-unstyled mb-0">
              <li style="display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid #F1F5F9;">
                <div style="display:flex;align-items:center;gap:10px;">
                  <img class="img-fluid" src="{{ url('front/images/cart/1.png') }}" alt="Group icon" style="width:40px;height:40px;border-radius:8px;object-fit:cover;">
                  <span style="font-size:.875rem;font-weight:600;color:#0F172A;">Community Watch</span>
                </div>
                <button style="background:#2563EB;color:#fff;border:none;border-radius:8px;padding:6px 14px;font-size:.8125rem;font-weight:600;cursor:pointer;">Join</button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Scripts -->
    <script async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAndFqevHboVWDN156vJqXk1Y1-D7QR7BE&callback=initMap"></script>
    <script src="{{ url('front/js/app.js') }}"></script>
    <script src="{{ url('front/js/bootstrap-datetimepicker.min.js') }}"></script>
    <script src="{{ url('front/js/noty.min.js') }}"></script>

    <script>
      /* Active nav item highlight */
      var url = window.location.href;
      var index_url = '{{ url("/") }}/';
      if (url !== index_url) {
        document.querySelectorAll('.sidebar-nav-item').forEach(function(link) {
          if (link.href && link.href.includes(url)) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
          }
        });
      } else {
        var homeLink = document.querySelector('.sidebar-nav-item[href="{{ url("/") }}"]');
        if (homeLink) homeLink.classList.add('active');
      }
    </script>

    <!-- Notification Vue instance -->
    <script>
      const notifApp = new Vue({
        el: '#notification-vue',
        data: {
          notifications: [],
          notification_count: 0,
          uri: base_url
        },
        methods: {
          get_notification() {
            var _this = this;
            axios.get(this.uri + '/get_notification').then(function(response) {
              _this.notifications = response.data.notifications;
              _this.notification_count = response.data.unread_notify;
            }).catch(error => console.log(error));
          }
        },
        created() {
          var _this = this;
          Echo.private('notification.' + {{ Auth::id() }})
            .listen('.notification.created', (e) => {
              _this.get_notification();
              _this.notification_count = _this.notification_count + 1;
              new Noty({
                type: 'success',
                theme: 'bootstrap-v3',
                layout: 'bottomRight',
                closeWith: ['click', 'button'],
                buttons: false,
                progressBar: true,
                text: e.message,
                animation: {
                  open: 'animated bounceInRight',
                  close: 'animated bounceOutRight'
                },
                sound: {
                  source: ['{{ asset("front/svg/nice-cut.wav") }}'],
                  volume: 1,
                  conditions: ['docVisible', 'docHidden']
                }
              }).show();
            })
            .listen('.ai.match.found', (e) => {
              _this.get_notification();
              _this.notification_count = _this.notification_count + 1;
              new Noty({
                type: 'warning',
                theme: 'bootstrap-v3',
                layout: 'bottomRight',
                closeWith: ['click', 'button'],
                buttons: false,
                progressBar: true,
                text: e.message || 'AI Match Found! Check post details for confidence score.',
                animation: {
                  open: 'animated bounceInRight',
                  close: 'animated bounceOutRight'
                }
              }).show();
            });
          _this.get_notification();
        }
      });
    </script>

    @stack('scripts')

  </body>
</html>
