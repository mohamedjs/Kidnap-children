<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Country extends Model
{
  protected $fillable = [
     'title' , 'lang','lat'
  ];

  public function country()
  {
      return $this->belongsTo('App\Country') ;
  }

  public function citys()
  {
    return $this->hasMany('App\City','country_id','id');
  }

  public function contents()
  {
    return $this->belongsToMany('App\Content','posts','operator_id','content_id')
    ->withPivot('id','published_date','active','patch_number','url','user_id')->withTimestamps();
  }

}
