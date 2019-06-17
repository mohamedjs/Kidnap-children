<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Region extends Model
{
  protected $fillable = [
      'title' , 'city_id' ,'lat','lang'
  ];

  public function city()
  {
      return $this->belongsTo('App\City') ;
  }
}
