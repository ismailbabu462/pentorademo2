#!/bin/bash

# Google Cloud VM'de Docker Compose ContainerConfig hatasını çözmek için script

echo "=== Docker Compose ContainerConfig Hatası Çözüm Scripti ==="
echo "Bu script Google Cloud VM'de çalıştırılmalıdır."
echo ""

# 1. Docker servisini kontrol et ve başlat
echo "1. Docker servisini kontrol ediliyor..."
sudo systemctl status docker
if [ $? -ne 0 ]; then
    echo "Docker servisi başlatılıyor..."
    sudo systemctl start docker
    sudo systemctl enable docker
fi

# 2. Mevcut container'ları durdur ve temizle
echo "2. Mevcut container'lar durduruluyor..."
docker-compose down --remove-orphans

# 3. Docker cache ve image'ları temizle
echo "3. Docker cache ve image'lar temizleniyor..."
docker system prune -a --volumes -f

# 4. Docker Compose cache'i temizle
echo "4. Docker Compose cache temizleniyor..."
docker-compose down --volumes --remove-orphans

# 5. Volume'ları temizle
echo "5. Volume'lar temizleniyor..."
docker volume prune -f

# 6. Network'leri temizle
echo "6. Network'ler temizleniyor..."
docker network prune -f

# 7. Production environment dosyasını kontrol et
echo "7. Environment dosyası kontrol ediliyor..."
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

# 8. Docker Compose'u production modunda çalıştır
echo "8. Docker Compose production modunda başlatılıyor..."
docker-compose -f docker-compose.prod.yml --env-file production.env up --build -d

# 9. Log'ları kontrol et
echo "9. Servis durumu kontrol ediliyor..."
sleep 10
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "=== Script tamamlandı ==="
echo "Eğer hala hata alıyorsanız, aşağıdaki komutları çalıştırın:"
echo "1. docker-compose -f docker-compose.prod.yml logs backend"
echo "2. docker-compose -f docker-compose.prod.yml logs mysql"
echo "3. docker-compose -f docker-compose.prod.yml logs nginx"
