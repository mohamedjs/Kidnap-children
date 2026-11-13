FROM php:7.4-fpm-alpine

WORKDIR /var/www/html

# Install system dependencies and PHP extensions required by Laravel
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

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Copy application files
COPY . /var/www/html

# Set up storage and cache permissions
RUN mkdir -p storage/framework/cache storage/framework/sessions storage/framework/views bootstrap/cache \
    && chown -R www-data:www-data storage bootstrap/cache \
    && chmod -R 775 storage bootstrap/cache \
    && chmod +x /var/www/html/docker/entrypoint.sh

EXPOSE 9000

ENTRYPOINT ["/var/www/html/docker/entrypoint.sh"]
CMD ["php-fpm"]
