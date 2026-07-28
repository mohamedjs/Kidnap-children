@extends('front.layout')
@section('page_title', 'Home Feed')

@section('content')
<div id="app" v-cloak>
  <vue-home :user="{{ Auth::user() }}"></vue-home>
</div>
@endsection
