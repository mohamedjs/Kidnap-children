@extends('front.layout')
@section('page_title') {{ Auth::user()->name }} @stop
@section('content')
  <div id="app">
    <inner-post-vue :user="{{ Auth::user() }}" :inner_post="{{ $post }}" :results="{{ $results }}"></inner-post-vue>
  </div>

@stop
