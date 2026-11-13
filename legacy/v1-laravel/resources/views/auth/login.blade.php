<!DOCTYPE html>
<html>
    <head>
      <title>Ecovve</title>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
      <!-- CSRF Token -->
      <meta name="csrf-token" content="{{ csrf_token() }}">
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
      <link rel="stylesheet" href="{{url('front/css/style.css')}}">
      <style media="screen">
      .cafe-page .cafe-background{
         background: url("{{url('front/images/cafe-background.png')}}") no-repeat center center;
      }
      .kayo-footer{
        background: url("{{url('front/images/footer_bg.jpg')}}") no-repeat center center;
      }
      .header {
        background: url("{{url('front/images/background.jpg')}}") no-repeat center center;
      }
      </style>
      <!--if lt IE 9 script(src='http://cdnjs.cloudflare.com/ajax/libs/es5-shim/2.0.8/es5-shim.min.js')-->
    </head>
  <body>
    <!-- start nav bar-->
    <nav class="cafe-navbar-container">
      <div class="cafe-navbar">
        <div class="bottom-nav">
          <div class="container">
            <nav class="navbar navbar-expand-lg navbar-light"><a class="navbar-brand" href="index.html"><img class="img-fluid" src="{{url('front/images/logo.png')}}"></a>
              <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button>
              <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav ml-auto">
                  <li class="nav-item"><a class="register-modal" href="#login-register" data-toggle="modal">REGISTER</a></li>
                  <li class="nav-item"><a class="login-modal" href="#login-register" data-toggle="modal">LOGIN</a></li>
                </ul>
              </div>
            </nav>
          </div>
        </div>
      </div>
      <div class="modal fade" id="login-register" tabindex="-1" role="dialog" aria-labelledby="cafeOfferTitle" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered" role="document">
          <div class="modal-content">
            <div class="register-login" id="login-content">
              <div class="row">
                <div class="col-lg-6 col-md-6 d-none d-xl-block d-lg-block office-img">
                  <div class="img-box"><img class="img-fluid" src="{{url('front/images/login-img.png')}}"></div>
                </div>
                <div class="col-lg-6">
                  <div class="register-box">
                    <h1 class="register-title">Welcome back :)</h1>
                    <p>To keep connected with us please login with your information Email or Phone number &amp; Password</p>
                    <form action="{{ route('login') }}" method="post">
                      @csrf
                      <div class="register-form login-form">
                        <div class="form-group">
                          <div class="icon-box"><i class="far fa-user"></i></div>
                          <div class="form-input">
                            <input class="form-control" type="email" name="email"><span class="form-holder">Phone Number OR Email</span>
                            @if ($errors->has('email'))
                                <span class="invalid-feedback" role="alert" style="display:block">
                                    <strong>{{ $errors->first('email') }}</strong>
                                </span>
                            @endif
                          </div>
                        </div>
                        <div class="form-group">
                          <div class="icon-box"><i class="fas fa-lock"></i></div>
                          <div class="form-input">
                            <input class="form-control" type="password" name="password"><span class="form-holder">Password</span>
                            @if ($errors->has('password'))
                                <span class="invalid-feedback" role="alert" style="display:block">
                                    <strong>{{ $errors->first('password') }}</strong>
                                </span>
                            @endif
                          </div>
                        </div>
                      </div>
                      <div class="login-option">
                        <label class="form-check-label">
                          <div class="custome-login-checkbox-group">
                            <input class="form-check-input" type="checkbox">
                            <div class="custome-login-checkbox"><i class="fas fa-check"></i></div>
                          </div><span>Remember Me!</span>
                        </label><a class="login-register-pagination forget" href="{{ route('password.request') }}" data-target="#forgetPassword-content">Forget Password?</a>
                      </div>
                      <button class="register-btn my-btn" type="submit">Login now!</button><a class="login-register-pagination register-modal login-btn my-btn" href="#" data-target="#register-content">Create Account</a>
                    </form>
                    <div class="social-links">
                      <p>Or login with</p>
                      <ul class="list-unstyled">
                        <li><a class="google" href="#"><img class="img-fluid" src="{{url('front/images/google-icon.png')}}"></a></li>
                        <li><a class="facebook" href="#"><i class="fab fa-facebook-f"></i></a></li>
                        <li><a class="twitter" href="#"><i class="fab fa-twitter"></i></a></li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
              <button class="close" type="button" data-dismiss="modal" aria-label="Close"><img src="{{url('front/images/icons/close.svg')}}"></button>
            </div>
            <div class="register-login" id="register-content">
              <div class="row">
                <div class="col-lg-6 col-md-6 d-none d-xl-block d-lg-block office-img">
                  <div class="img-box"><img class="img-fluid" src="{{url('front/images/office.png')}}"></div>
                </div>
                <div class="col-lg-6">
                  <div class="register-box">
                    <h1 class="register-title">Welcome To Ecovve!</h1>
                    <p>it is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.</p>
                    <form action="{{ route('register') }}" method="post">
                      @csrf
                      <div class="register-form register">
                        <div class="form-group active">
                          <div class="icon-box"><i class="far fa-user"></i></div>
                          <div class="form-input">
                            <input class="form-control" type="text" name="name"><span class="form-holder">Full Name</span>
                            @if ($errors->has('name'))
                                <span class="invalid-feedback" role="alert" style="display:block">
                                    <strong>{{ $errors->first('name') }}</strong>
                                </span>
                            @endif
                          </div>
                        </div>
                        <div class="form-group">
                          <div class="icon-box"><i class="far fa-envelope"></i></div>
                          <div class="form-input">
                            <input class="form-control" type="email" name="email"><span class="form-holder">Email Address</span>
                            @if ($errors->has('email'))
                                <span class="invalid-feedback" role="alert" style="display:block">
                                    <strong>{{ $errors->first('email') }}</strong>
                                </span>
                            @endif
                          </div>
                        </div>
                        <div class="form-group">
                          <div class="icon-box"><i class="fas fa-phone"></i></div>
                          <div class="form-input">
                            <input class="form-control" type="text" name="phone"><span class="form-holder">Phone</span>
                            @if ($errors->has('phone'))
                                <span class="invalid-feedback" role="alert" style="display:block">
                                    <strong>{{ $errors->first('phone') }}</strong>
                                </span>
                            @endif
                          </div>
                        </div>
                        <div class="form-group">
                          <div class="icon-box"><i class="fas fa-map-marker-alt"></i></div>
                          <div class="form-input">
                            <input class="form-control" type="text" name="address"><span class="form-holder">Address</span>
                            @if ($errors->has('address'))
                                <span class="invalid-feedback" role="alert" style="display:block">
                                    <strong>{{ $errors->first('address') }}</strong>
                                </span>
                            @endif
                          </div>
                        </div>
                        <div class="form-group">
                          <div class="icon-box"><i class="fas fa-lock"></i></div>
                          <div class="form-input">
                            <input class="form-control" type="password" name="password"><span class="form-holder">Password</span>
                            @if ($errors->has('password'))
                                <span class="invalid-feedback" role="alert" style="display:block">
                                    <strong>{{ $errors->first('password') }}</strong>
                                </span>
                            @endif
                          </div>
                        </div>
                      </div>
                      <button class="register-btn my-btn" type="submit" >Sign Up Now!</button><a class="login-register-pagination login-modal login-btn my-btn" href="#" data-target="#login-content">Get Login!</a>
                    </form>
                    <div class="social-links">
                      <p>Or you can join with</p>
                      <ul class="list-unstyled">
                        <li><a class="google" href="#"><img class="img-fluid" src="{{url('front/images/google-icon.png')}}"></a></li>
                        <li><a class="facebook" href="#"><i class="fab fa-facebook-f"></i></a></li>
                        <li><a class="twitter" href="#"><i class="fab fa-twitter"></i></a></li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
              <button class="close" type="button" data-dismiss="modal" aria-label="Close"><img src="{{url('front/images/icons/close.svg')}}"></button>
            </div>
            <div class="register-login" id="forgetPassword-content">
              <div class="row">
                <div class="col-lg-6 col-md-6 d-none d-xl-block d-lg-block office-img">
                  <div class="img-box"><img class="img-fluid" src="{{url('front/images/office.png')}}"></div>
                </div>
                <div class="col-lg-6">
                  <div class="register-box">
                    <h1 class="register-title">Forget Password!</h1>
                    <p>Please enter your Email or phone number to reset your password</p>
                    <form action="">
                      <div class="register-form register">
                        <div class="form-group">
                          <div class="icon-box"><i class="far fa-user"></i></div>
                          <div class="form-input">
                            <input class="form-control" type="text"><span class="form-holder">Phone Number OR Email</span>
                          </div>
                        </div>
                      </div>
                      <button class="login-register-pagination register-btn my-btn" type="submit" data-target="#ResetPasswordCode-content">Reset Password!</button><a class="login-modal login-btn my-btn" href="#">Get Login!</a>
                    </form>
                  </div>
                </div>
              </div>
              <button class="close" type="button" data-dismiss="modal" aria-label="Close"><img src="{{url('front/images/icons/close.svg')}}"></button>
            </div>
            <div class="register-login" id="ResetPasswordCode-content">
              <div class="row">
                <div class="col-lg-6 col-md-6 d-none d-xl-block d-lg-block office-img">
                  <div class="img-box"><img class="img-fluid" src="{{url('front/images/office.png')}}"></div>
                </div>
                <div class="col-lg-6">
                  <div class="register-box">
                    <h1 class="register-title">Forget Password!</h1>
                    <p>We have sent an activation code to your phone number please enter it below to confirmation</p>
                    <form action="">
                      <div class="register-form register">
                        <div class="form-group">
                          <div class="icon-box"><i class="fab fa-slack-hash"></i></div>
                          <div class="form-input">
                            <input class="form-control" type="text"><span class="form-holder">Confirmation Code</span>
                          </div>
                        </div>
                      </div>
                      <button class="login-register-pagination register-btn my-btn" type="submit" data-target="#newPassword-content">Reset Password!</button><a class="login-modal login-btn my-btn" href="#">Get Login!</a>
                      <div class="mt-4"><a class="resend-code" href="#"><i class="fas fa-redo-alt"></i><span>Resend Code</span><span class="send-after">after:</span><span class="send-after">00:25</span></a></div>
                    </form>
                  </div>
                </div>
              </div>
              <button class="close" type="button" data-dismiss="modal" aria-label="Close"><img src="{{url('front/images/icons/close.svg')}}"></button>
            </div>
            <div class="register-login" id="newPassword-content">
              <div class="row">
                <div class="col-lg-6 col-md-6 d-none d-xl-block d-lg-block office-img">
                  <div class="img-box"><img class="img-fluid" src="{{url('front/images/office.png')}}"></div>
                </div>
                <div class="col-lg-6">
                  <div class="register-box">
                    <h1 class="register-title">Forget Password!</h1>
                    <p>Please enter your Email or phone number to reset your password</p>
                    <form action="">
                      <div class="register-form register">
                        <div class="form-group">
                          <div class="icon-box"><i class="fas fa-lock"></i></div>
                          <div class="form-input">
                            <input class="form-control" type="password"><span class="form-holder">Password</span>
                          </div>
                        </div>
                        <div class="form-group">
                          <div class="icon-box"><i class="fas fa-lock"></i></div>
                          <div class="form-input">
                            <input class="form-control" type="password"><span class="form-holder">Confirm Password</span>
                          </div>
                        </div>
                      </div><a class="login-register-pagination register-btn my-btn" href="#" data-target="#login-content">Reset Password!</a>
                    </form>
                  </div>
                </div>
              </div>
              <button class="close" type="button" data-dismiss="modal" aria-label="Close"><img src="{{url('front/images/icons/close.svg')}}"></button>
            </div>
            <div class="register-login" id="activateMobileCode-content">
              <div class="row">
                <div class="col-lg-6 col-md-6 d-none d-xl-block d-lg-block office-img">
                  <div class="img-box"><img class="img-fluid" src="{{url('front/images/office.png')}}"></div>
                </div>
                <div class="col-lg-6">
                  <div class="register-box">
                    <h1 class="register-title">Confirm Phone Number!</h1>
                    <p>we have sent activation code to your phone number please enter it below</p>
                    <form action="home.html">
                      <div class="register-form register">
                        <div class="form-group">
                          <div class="icon-box"><i class="fab fa-slack-hash"></i></div>
                          <div class="form-input">
                            <input class="form-control" type="text"><span class="form-holder">Confirmation Code</span>
                          </div>
                        </div>
                      </div>
                      <button class="register-btn my-btn" type="submit">Activate Phone</button><a class="login-register-pagination login-btn my-btn" href="#" data-target="#changePhoneNumber-content">Change Phone Number</a>
                      <div class="mt-4"><a class="resend-code" href="#"><i class="fas fa-redo-alt"></i><span>Resend Code</span><span class="send-after">after:</span><span class="send-after">00:25</span></a></div>
                    </form>
                  </div>
                </div>
              </div>
              <button class="close" type="button" data-dismiss="modal" aria-label="Close"><img src="{{url('front/images/icons/close.svg')}}"></button>
            </div>
            <div class="register-login" id="changePhoneNumber-content">
              <div class="row">
                <div class="col-lg-6 col-md-6 d-none d-xl-block d-lg-block office-img">
                  <div class="img-box"><img class="img-fluid" src="{{url('front/images/office.png')}}"></div>
                </div>
                <div class="col-lg-6">
                  <div class="register-box">
                    <h1 class="register-title">Confirm Phone Number!</h1>
                    <p>we have sent activation code to your phone number please enter it below</p>
                    <form action="">
                      <div class="register-form register">
                        <div class="form-group">
                          <div class="icon-box"><i class="fas fa-phone"></i></div>
                          <div class="form-input">
                            <input class="form-control" type="text"><span class="form-holder">Phone</span>
                          </div>
                        </div>
                      </div>
                      <button class="login-register-pagination register-btn my-btn" type="submit" data-target="#activateMobileCode-content">Activate Phone</button>
                    </form>
                  </div>
                </div>
              </div>
              <button class="close" type="button" data-dismiss="modal" aria-label="Close"><img src="{{url('front/images/icons/close.svg')}}"></button>
            </div>
          </div>
        </div>
      </div>
    </nav>
    <!-- end nav bar-->
    <!-- start header-->
    <div class="header">
      <div class="overlay">
        <div class="container">
          <h1 class="title text-center">We Help You <span>To Find Missed People </span>And Contact Them
          </h1>
        </div>
      </div>
    </div>
    <div class="address-modal modal fade" id="location-by-map" tabindex="-1" role="dialog" aria-labelledby="cafeOfferTitle" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content show-add-address-modal-content">
          <div class="modal-header">
            <div class="d-flex justify-content-start">
              <h5 class="modal-title" id="exampleModalLongTitle">Add Your Location</h5>
            </div>
            <button class="close" type="button" data-dismiss="modal" aria-label="Close"><img src="{{url('front/images/icons/close.svg')}}"></button>
            <div class="clearfix"></div>
          </div>
          <div class="map-content modal-body">
            <div class="content-box"><img class="img-fluid" src="{{url('front/images/map.jpg')}}">
              <div class="form-group">
                <input class="form-control" type="text" placeholder="Search For Address"><i class="icon-search fas fa-search"></i>
              </div>
              <div class="address-btn-group d-flex justify-content-between"><a class="address-btn confirm-location" href="#">CONFIRM LOCATION</a></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- end header-->
    <!-- script tags-->
    <div id="app">

    </div>
    <script src="{{url('front/js/app.js')}}"></script>
  </body>
</html>
