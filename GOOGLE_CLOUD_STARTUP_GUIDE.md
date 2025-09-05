# Google Cloud VM Production Startup Guide

Bu rehber, Pentest Suite uygulamasını Google Cloud VM'de production modunda başlatmak için gerekli tüm adımları içerir.

## 🚀 Hızlı Başlangıç

### 1. VM'ye Bağlan
```bash
gcloud compute ssh [VM-INSTANCE-NAME] --zone=[ZONE]
```

### 2. Projeyi Kopyala
```bash
# Projeyi VM'ye kopyala
gcloud compute scp --recurse ./app [VM-INSTANCE-NAME]:~/ --zone=[ZONE]

# VM'ye bağlan
gcloud compute ssh [VM-INSTANCE-NAME] --zone=[ZONE]

# Proje dizinine git
cd ~/app
```

### 3. Gerekli Araçları Yükle
```bash
# Docker yükle
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose yükle
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Python bağımlılıkları yükle
sudo apt update
sudo apt install -y python3-pip python3-venv
pip3 install requests psutil
```

### 4. Scriptleri Çalıştırılabilir Yap
```bash
chmod +x *.sh *.py
chmod +x backend/scripts/*.py
chmod +x DesktopAgent/*.py
```

## 🎯 Başlatma Seçenekleri

### Seçenek 1: Hızlı Başlatma (Önerilen)
```bash
python3 quick-start.py
```

### Seçenek 2: Detaylı Başlatma
```bash
python3 start-production.py
```

### Seçenek 3: Manuel Başlatma
```bash
# 1. Güvenli şifreler oluştur
./generate-secrets.sh

# 2. Servisleri başlat
docker-compose -f docker-compose.prod.yml --env-file production.env up -d

# 3. Desktop Agent'ı başlat
cd DesktopAgent
python3 agent.py &
cd ..

# 4. Durumu kontrol et
docker-compose -f docker-compose.prod.yml --env-file production.env ps
```

## 🔧 Servis Yönetimi

### Servisleri Durdur
```bash
docker-compose -f docker-compose.prod.yml --env-file production.env down
```

### Logları Görüntüle
```bash
# Tüm servisler
docker-compose -f docker-compose.prod.yml --env-file production.env logs

# Belirli bir servis
docker-compose -f docker-compose.prod.yml --env-file production.env logs backend
```

### Servisleri Yeniden Başlat
```bash
docker-compose -f docker-compose.prod.yml --env-file production.env restart
```

## 🌐 Erişim URL'leri

- **Frontend**: `https://pentorasecbeta.mywire.org`
- **API**: `https://pentorasecbeta.mywire.org/api`
- **Health Check**: `https://pentorasecbeta.mywire.org/health`
- **Desktop Agent**: `ws://pentorasecbeta.mywire.org:13337`
- **Desktop Agent Health**: `http://pentorasecbeta.mywire.org:13338/health`

## 🔒 Güvenlik Ayarları

### Firewall Kuralları
```bash
# HTTP ve HTTPS trafiğine izin ver
gcloud compute firewall-rules create allow-http-https \
    --allow tcp:80,tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTP and HTTPS traffic"

# Desktop Agent portu
gcloud compute firewall-rules create allow-desktop-agent \
    --allow tcp:13337,tcp:13338 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Desktop Agent traffic"
```

### SSL Sertifikası
```bash
# Let's Encrypt sertifikası al
./init-letsencrypt.sh -d pentorasecbeta.mywire.org -e admin@pentorasecbeta.mywire.org

# Sertifikaları yenile
./renew-certs.sh
```

## 📊 Monitoring ve Bakım

### Otomatik Başlatma (Systemd)
```bash
# Service dosyasını kopyala
sudo cp pentest-suite.service /etc/systemd/system/

# Servisi etkinleştir
sudo systemctl enable pentest-suite.service
sudo systemctl start pentest-suite.service

# Durumu kontrol et
sudo systemctl status pentest-suite.service
```

### Health Check
```bash
# Tüm servislerin durumunu kontrol et
python3 verify-production.py

# Integration test
python3 test-integration.py
```

### Log Rotation
```bash
# Log dosyalarını temizle
sudo logrotate -f /etc/logrotate.conf

# Docker logları temizle
docker system prune -f
```

## 🚨 Sorun Giderme

### Servis Başlamıyor
```bash
# Docker durumunu kontrol et
sudo systemctl status docker

# Port çakışması kontrol et
netstat -tulpn | grep :80
netstat -tulpn | grep :443
netstat -tulpn | grep :13337

# Logları kontrol et
docker-compose -f docker-compose.prod.yml --env-file production.env logs
```

### Database Bağlantı Sorunu
```bash
# MySQL container'ını kontrol et
docker-compose -f docker-compose.prod.yml --env-file production.env logs mysql

# Database'e bağlan
docker-compose -f docker-compose.prod.yml --env-file production.env exec mysql mysql -u root -p
```

### SSL Sertifika Sorunu
```bash
# Sertifika dosyalarını kontrol et
ls -la /etc/letsencrypt/live/pentorasecbeta.mywire.org/

# Nginx konfigürasyonunu test et
docker-compose -f docker-compose.prod.yml --env-file production.env exec nginx nginx -t
```

## 📈 Performans Optimizasyonu

### VM Kaynakları
- **Minimum**: 2 vCPU, 4GB RAM, 20GB SSD
- **Önerilen**: 4 vCPU, 8GB RAM, 50GB SSD
- **Production**: 8 vCPU, 16GB RAM, 100GB SSD

### Docker Optimizasyonu
```bash
# Docker daemon konfigürasyonu
sudo nano /etc/docker/daemon.json

# İçerik:
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}

# Docker'ı yeniden başlat
sudo systemctl restart docker
```

## 🔄 Backup ve Restore

### Database Backup
```bash
# Backup oluştur
docker-compose -f docker-compose.prod.yml --env-file production.env exec mysql mysqldump -u root -p pentest_suite > backup.sql

# Backup'ı geri yükle
docker-compose -f docker-compose.prod.yml --env-file production.env exec -T mysql mysql -u root -p pentest_suite < backup.sql
```

### Volume Backup
```bash
# Tüm volume'ları backup'la
docker run --rm -v pentest_mysql_data:/data -v $(pwd):/backup alpine tar czf /backup/mysql_data.tar.gz -C /data .
docker run --rm -v pentest_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
```

## 📞 Destek

Sorun yaşarsanız:
1. Logları kontrol edin
2. `python3 verify-production.py` çalıştırın
3. `python3 test-integration.py` çalıştırın
4. GitHub Issues'da sorun bildirin

---

**Not**: Bu rehber Google Cloud VM için optimize edilmiştir. Diğer cloud sağlayıcıları için bazı komutlar farklı olabilir.
