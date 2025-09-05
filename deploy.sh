#!/bin/bash

echo "=== Google Cloud VM Deploy Script ==="

# Environment dosyasını kontrol et
if [ ! -f "production.env" ]; then
    echo "production.env dosyası bulunamadı, oluşturuluyor..."
    cat > production.env << EOF
MYSQL_ROOT_PASSWORD=secure_root_password_$(date +%s)
MYSQL_PASSWORD=secure_password_$(date +%s)
LEMONSQUEEZY_WEBHOOK_SECRET=pentora_webhook_secret_2024
GOOGLE_API_KEY=
SEARCH_ENGINE_ID=
EOF
fi

# Docker servisini başlat
sudo systemctl start docker

# Mevcut container'ları durdur
docker-compose -f docker-compose.prod.yml down --remove-orphans

# Cache'i temizle
docker system prune -a --volumes -f

# Production modunda başlat
docker-compose -f docker-compose.prod.yml --env-file production.env up --build -d

# Durumu kontrol et
sleep 10
docker-compose -f docker-compose.prod.yml ps

echo "Deploy tamamlandı!"
