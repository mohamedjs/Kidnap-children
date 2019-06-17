@extends('front.layout')
@section('page_title') {{ Auth::user()->name }} @stop
@section('content')
  <div class="dashboard-profile-content customer-dashboard-scroll-60 perfect-scroll">
    <div class="cover-box">
        <div class="profile-info">
          <div class="overlay">
            <div class="profile-photo"><img class="img-fluid" src="{{ Auth::user()->image }}"></div>
            <p class="profile-name">{{ Auth::user()->name }}</p>
            <ul class="profile-setting list-unstyled">
              <li><a class="setting-item" href="#"><i class="fas fa-user-plus"></i></a></li>
              <li><a class="setting-item" href="customer-chat.html"><i class="fas fa-comments"></i></a></li>
              <li>
                <div class="dropdown show setting-dropdown"><a class="setting-item" href="#" role="button" id="profile-setting-dropdown" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"><i class="fas fa-ellipsis-h"></i></a>
                  <div class="dropdown-menu" aria-labelledby="profile-setting-dropdown"><a class="dropdown-item" href="#" data-toggle="modal" data-target="#add-to-group">Add to group</a><a class="dropdown-item" href="#">Unfriend</a><a class="dropdown-item" href="#">Block</a><a class="dropdown-item" href="customer-profile__editProfile.html">Edit Profile</a></div>
                </div>
              </li>
            </ul>
          </div>
        </div>
        <div class="profile-links">
          <ul class="profile-tab nav-tabs list-unstyled" id="profile-tab">
            <li class="nav-item"><a class="nav-link active" id="profile-friend" href="{{ url('profile') }}">My Posts</a></li>
            <li class="nav-item"><a class="nav-link" id="profile-about" href="{{ url('profile') }}">About</a></li>
          </ul>
        </div>
        <div class="profile-content">
        <div id="about-profile">
          <div class="about-me-tab">
            <div class="bg-fff shadow-15 round-10">
              <h1 class="fz-16 fw-b heading">About
                <button form="form1" class="save float-right"><i class="fas fa-check"></i>Save
                </button>
              </h1>
              <hr class="grey">
              <form action="{{ url('user') }}" method="post" id="form1" enctype="multipart/form-data">
                @csrf
                <div class="row fields">
                  <div class="col-sm-6 col-xs-12">
                    <div class="field email-field">
                      <div class="icon"><i class="far fa-envelope"></i></div>
                      <input class="label" name="email" type="email" value="{{Auth::user()->email}}">
                    </div>
                  </div>
                  <div class="col-sm-6 col-xs-12">
                    <div class="field phone-field">
                      <div class="icon"><i class="fas fa-phone"></i></div>
                      <input class="label" name="phone" type="text" value="{{ Auth::user()->phone }}">
                    </div>
                  </div>
                  <div class="col-sm-6 col-xs-12">
                    <div class="field gender-field">
                      <select class="destory-selectize" id="select-gender" name="gender" placeholder="Pick some links...">
                        <option value="1" @if(Auth::user()->gender) selected @endif>Male</option>
                        <option value="2" @if(Auth::user()->gender) selected @endif>Female</option>
                      </select>
                    </div>
                  </div>
                  <div class="col-sm-6 col-xs-12">
                    <div class="field birthday-field">
                      <div class="icon"><i class="fas fa-birthday-cake"></i></div>
                      <input class="label date" name="birth_date" type="text" id="datepicker" value="{{ Auth::user()->birth_date }}">
                    </div>
                  </div>
                  <div class="col-sm-6 col-xs-12">
                    <div class="field birthday-field">
                      <div class="icon"><i class="fas fa-marker"></i></div>
                      <input class="label" name="address" type="text" value="{{Auth::user()->address}}">
                    </div>
                  </div>
                  <div class="col-sm-6 col-xs-12">
                    <div class="field birthday-field">
                      <div class="icon"><i class="fab fa-accessible-icon"></i></div>
                      <input class="label" name="age" type="text" value="{{Auth::user()->age}}">
                    </div>
                  </div>
                  <div class="col-sm-6 col-xs-12">
                    <div class="field birthday-field">
                      <div class="icon"><i class="fas fa-copy"></i></div>
                      <input class="label" name="user_image" type="file">
                    </div>
                  </div>
                  <div class="col-sm-6 col-xs-12">
                    <div class="field birthday-field">
                      <div class="icon"><i class="fas fa-copy"></i></div>
                      <input class="label" name="user_background_image" type="file">
                    </div>
                  </div>
                </div>
              </form>
              <div class="media-links">
                <h1 class="fz-16 fw-b heading">Social Media</h1>
                <div class="links" id="socialLinks">
                  <div class="link-item">
                    <input class="input" type="text" value="http://facebook.com/prog.karem.tarek" placeholder="Social Media Link">
                    <select class="input select" name="select-time" placeholder="Social Media">
                      <option value="">Social Media</option>
                      <option value="1" selected>Facebook</option>
                      <option value="2">Twitter</option>
                      <option value="3">Youtube</option>
                      <option value="4">Linked in</option>
                      <option value="5">Instagram</option>
                    </select><a class="delete" href="#"><i class="fas fa-times"></i></a>
                  </div>
                  <div class="link-item">
                    <input class="input" type="text" value="http://instagram.com/mrkayo" placeholder="Social Media Link">
                    <select class="input select" name="select-time" placeholder="Social Media">
                      <option value="">Social Media</option>
                      <option value="1">Facebook</option>
                      <option value="2">Twitter</option>
                      <option value="3">Youtube</option>
                      <option value="4">Linked in</option>
                      <option value="5" selected>Instagram</option>
                    </select><a class="delete" href="#"><i class="fas fa-times"></i></a>
                  </div>
                  <div class="link-item">
                    <input class="input" type="text" value="http://youtube.com/mrkayo" placeholder="Social Media Link">
                    <select class="input select" name="select-time" placeholder="Social Media">
                      <option value="">Social Media</option>
                      <option value="1">Facebook</option>
                      <option value="2">Twitter</option>
                      <option value="3" selected>Youtube</option>
                      <option value="4">Linked in</option>
                      <option value="5">Instagram</option>
                    </select><a class="delete" href="#"><i class="fas fa-times"></i></a>
                  </div>
                  <div class="link-item">
                    <input class="input" type="text" value="http://twitter.com/prog.karem.tarek" placeholder="Social Media Link">
                    <select class="input select" name="select-time" placeholder="Social Media">
                      <option value="">Social Media</option>
                      <option value="1">Facebook</option>
                      <option value="2" selected>Twitter</option>
                      <option value="3">Youtube</option>
                      <option value="4">Linked in</option>
                      <option value="5">Instagram</option>
                    </select><a class="delete" href="#"><i class="fas fa-times"></i></a>
                  </div>
                  <div class="link-item">
                    <input class="input" type="text" value="http://instagram.com/prog.karem.tarek" placeholder="Social Media Link">
                    <select class="input select" name="select-time" placeholder="Social Media">
                      <option value="">Social Media</option>
                      <option value="1">Facebook</option>
                      <option value="2">Twitter</option>
                      <option value="3">Youtube</option>
                      <option value="4">Linked in</option>
                      <option value="5" selected>Instagram</option>
                    </select><a class="delete" href="#"><i class="fas fa-times"></i></a>
                  </div>
                </div><a class="add-new" id="addNewSocial" href="#">
                  <div class="circle"><i class="fa fa-plus"></i></div>Add New Social Link</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
@stop
