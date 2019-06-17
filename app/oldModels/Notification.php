<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Notification extends Model
{
  protected $fillable = [
      'send_id' , 'receive_id'  , 'title' , 'content' ,'seen'
  ];
}
