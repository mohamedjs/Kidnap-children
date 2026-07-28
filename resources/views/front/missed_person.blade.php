@extends('front.layout')
@section('page_title', 'Missing Children')

@section('content')
<div id="app" v-cloak>
  <missed-person-vue :user="{{ Auth::user() }}"></missed-person-vue>
</div>
@endsection
