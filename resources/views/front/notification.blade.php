@extends('front.layout')
@section('page_title') {{ Auth::user()->name }} @stop
@section('content')
  <div class="dashboard-notification-page" style="padding-top:10%">
    <div class="bg-fff round-20 ov-h">
      <div class="stipped-rows">
        <ul class="list-unstyled mb-0">
          @foreach ($notifications as $key => $notification)
            <li><a class="notification-row" href="{{ $notification->notification_url }}">
                <div class="round-10 img"><img class="img-fluid" src="{{ $notification->sender->image }}"></div>
                <div class="info">
                  <h3 class="brand">{{ $notification->sender->name }}</h3>
                  <div class="subline"><span class="time">{{$notification->created_at->diffForHumans()}}</span><span class="title">{{ $notification->content }}</span></div>
                </div></a></li>
          @endforeach

        </ul>
      </div>
    </div>
  </div>
@stop
