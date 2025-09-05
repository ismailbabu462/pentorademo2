# Google Cloud VM Deployment Guide

## ContainerConfig Hatası Çözümü

Bu hata genellikle Docker image'larının bozuk olması veya Docker cache problemlerinden kaynaklanır.

### 1. Google Cloud VM'ye Bağlanın

```bash
# SSH ile VM'ye bağlanın
gcloud compute ssh [VM-INSTANCE-NAME] --zone=[ZONE]
```

### 2. Proje Dosyalarını VM'ye Kopyalayın

```bash
# Local makinenizden VM'ye dosyaları kopyalayın
gcloud compute scp --recurse ./app [VM-INSTANCE-NAME]:~/ --zone=[ZONE]
```

### 3. VM'de Docker Kurulumunu Kontrol Edin

```bash
# Docker'ın kurulu olduğundan emin olun
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### 4. ContainerConfig Hatasını Çözün

```bash
# Proje dizinine gidin
cd ~/app

# Mevcut container'ları durdurun
docker-compose -f docker-compose.prod.yml down --remove-orphans

# Docker cache'i temizleyin
docker system prune -a --volumes -f

# Volume'ları temizleyin
docker volume prune -f

# Network'leri temizleyin
docker network prune -f

# Production environment dosyasını oluşturun
cat > production.env << EOF
MYSQL_ROOT_PASSWORD=secure_root_password_$(date +%s)
MYSQL_PASSWORD=secure_password_$(date +%s)
LEMONSQUEEZY_WEBHOOK_SECRET=pentora_webhook_secret_2024
GOOGLE_API_KEY=your_google_api_key_here
SEARCH_ENGINE_ID=your_search_engine_id_here
EOF

# Docker Compose'u production modunda çalıştırın
docker-compose -f docker-compose.prod.yml --env-file production.env up --build -d
```

### 5. Servis Durumunu Kontrol Edin

```bash
# Container'ların durumunu kontrol edin
docker-compose -f docker-compose.prod.yml ps

# Log'ları kontrol edin
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs mysql
docker-compose -f docker-compose.prod.yml logs nginx
```

### 6. Firewall Kurallarını Ayarlayın

```bash
# HTTP ve HTTPS portlarını açın
gcloud compute firewall-rules create allow-http-https \
    --allow tcp:80,tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server,https-server
```

### 7. SSL Sertifikası Kurulumu

```bash
# Certbot ile SSL sertifikası alın
docker-compose -f docker-compose.prod.yml run --rm certbot

# Nginx'i yeniden başlatın
docker-compose -f docker-compose.prod.yml restart nginx
```

## Sorun Giderme

### ContainerConfig Hatası Devam Ederse

```bash
# Docker'ı tamamen yeniden başlatın
sudo systemctl restart docker

# Docker daemon'ı temizleyin
sudo rm -rf /var/lib/docker
sudo systemctl restart docker

# Tekrar deneyin
docker-compose -f docker-compose.prod.yml --env-file production.env up --build -d
```

### Memory Hatası Alırsanız

```bash
# Swap alanı ekleyin
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Database Bağlantı Hatası

```bash
# MySQL container'ının log'larını kontrol edin
docker-compose -f docker-compose.prod.yml logs mysql

# Database'i yeniden oluşturun
docker-compose -f docker-compose.prod.yml down
docker volume rm app_mysql_data
docker-compose -f docker-compose.prod.yml --env-file production.env up -d mysql
```

## Otomatik Deploy Script

```bash
#!/bin/bash
# deploy.sh

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
```

## Önemli Notlar

1. **Güvenlik**: Production environment'ta güçlü şifreler kullanın
2. **Backup**: Düzenli olarak database backup'ı alın
3. **Monitoring**: Container log'larını düzenli olarak kontrol edin
4. **Updates**: Docker image'larını düzenli olarak güncelleyin

## Destek

Sorun yaşarsanız:
1. `docker-compose -f docker-compose.prod.yml logs` komutunu çalıştırın
2. Container durumunu `docker ps -a` ile kontrol edin
3. VM'nin memory ve disk kullanımını kontrol edin
