<?php

namespace App\Http\Middleware;

use Closure;

class SetLocaleLanguage
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
//        $params = $request->route()->parameter('locale');
//        app()->setLocale($params);
//        return $next($request);
        
        
        if($request->method() === 'GET' or $request->method() === 'POST'){
            $segment = ($request->segment(1) != 'api' )? $request->segment(1) : $request->segment(2);
                \Carbon\Carbon::setLocale('en');
            if (!in_array($segment,config('app.locales'))) {
                $segments = $request->segments();

                $fallback = app()->getLocale();

                $segments = array_prepend($segments,$fallback);

                \Carbon\Carbon::setLocale(app()->getLocale());

                return redirect()->to(implode('/',$segments));
            }

            app()->setLocale($segment);
            \Carbon\Carbon::setLocale(app()->getLocale());
        }

        return $next($request);
    }
}
