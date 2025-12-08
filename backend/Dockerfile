FROM php:8.2-cli

RUN apt-get update && apt-get install -y \
    zip unzip git curl \
    && docker-php-ext-install pdo pdo_mysql

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html
