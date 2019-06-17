<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use App\Models\User;

class Notification extends Model
{
  protected $fillable = [
      'send_id' , 'receive_id','title' , 'content' , 'notification_url' ,'seen'
  ];

  public function sender()
  {
      return $this->belongsTo('App\Models\User','send_id') ;
  }
  public function receiver()
  {
      return $this->belongsTo('App\Models\User','receive_id') ;
  }

}
