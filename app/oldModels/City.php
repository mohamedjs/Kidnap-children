<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class City extends Model
{
  protected $fillable = [
      'country_id' , 'title' , 'lang','lat'
  ];

  public function country()
  {
      return $this->belongsTo('App\Country') ;
  }

  public function regions()
  {
    return $this->hasMany('App\Region','city_id','id');
  }
}
