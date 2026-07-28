#!/bin/sh
set -e

if [ ! -f "/var/www/html/vendor/autoload.php" ]; then
    echo "Installing composer dependencies..."
    composer install --no-interaction --prefer-dist --optimize-autoloader || composer dump-autoload
fi

exec "$@"
