<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class SuggestUser extends Model
{
  protected $fillable = [
      'user_id' ,'suggest_id', 'priority'
  ];
}
