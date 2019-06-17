<?php

namespace App\Http\Middleware;

use Closure;
use App;
use Illuminate\Http\Request;
class HttpsProtocol
{
    /**
     * Handle an incoming request.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure  $next
     * @return mixed
     */
    public function handle($request, Closure $next)
    {

        if (!$request->secure() && App::environment() === 'production') {
            $request->setTrustedProxies( [ $request->getClientIp() ] , Request:: HEADER_X_FORWARDED_AWS_ELB);
            return redirect()->secure($request->getRequestUri());
        }

            return $next($request);
    }
}
