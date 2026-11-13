FROM php:7.4-fpm-alpine

WORKDIR /var/www/html

RUN apk add --no-cache \
    curl \
    libpng-dev \
    libjpeg-turbo-dev \
    freetype-dev \
    libzip-dev \
    oniguruma-dev \
    icu-dev \
    mysql-client \
    bash

RUN docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j$(nproc) pdo pdo_mysql mbstring gd zip bcmath opcache

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

COPY . /var/www/html

RUN mkdir -p storage/framework/cache storage/framework/sessions storage/framework/views bootstrap/cache \
    && chown -R www-data:www-data storage bootstrap/cache \
    && chmod +x /var/www/html/docker/entrypoint.sh

ENTRYPOINT ["/var/www/html/docker/entrypoint.sh"]
CMD ["sh", "-c", "while true; do php artisan schedule:run --no-interaction; sleep 60; done"]
