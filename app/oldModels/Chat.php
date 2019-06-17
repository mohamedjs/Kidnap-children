<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Chat extends Model
{
  protected $fillable = [
      'send_id' ,'receive_id', 'message' ,'seen','message_type'
  ];
}
