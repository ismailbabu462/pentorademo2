# Nginx + Certbot Setup Guide

Bu rehber, Pentest Suite uygulamasını Caddy'den Nginx + Certbot'a geçirmek için gerekli adımları açıklar.

## 🚀 Hızlı Başlangıç

### 1. Self-Signed Certificate ile Başlatma

```bash
# Self-signed certificate oluştur
./nginx/ssl-setup.sh

# Servisleri başlat
docker-compose up -d
```

### 2. Production SSL Certificate Alma

```bash
# Let's Encrypt certificate al
./init-letsencrypt.sh -d pentorasecbeta.mywire.org -e admin@pentorasecbeta.mywire.org
```

## 📁 Dosya Yapısı

```
├── nginx/
│   ├── conf.d/
│   │   └── default.conf          # Nginx konfigürasyonu
│   └── ssl-setup.sh              # Self-signed certificate scripti
├── certbot/
│   ├── conf/                     # Let's Encrypt sertifikaları
│   ├── www/                      # Webroot challenge
│   └── logs/                     # Certbot logları
├── init-letsencrypt.sh           # SSL sertifika alma scripti
└── docker-compose.yml            # Güncellenmiş Docker Compose
```

## 🔧 Konfigürasyon

### Nginx Özellikleri

- **Reverse Proxy**: Backend ve Frontend servislerini yönetir
- **SSL Termination**: HTTPS trafiğini işler
- **Rate Limiting**: API isteklerini sınırlar
- **Security Headers**: Güvenlik başlıkları ekler
- **Gzip Compression**: Dosya sıkıştırması
- **Health Checks**: Servis sağlık kontrolleri

### SSL Sertifika Yönetimi

- **Self-Signed**: İlk kurulum için geçici sertifika
- **Let's Encrypt**: Production için ücretsiz SSL
- **Auto Renewal**: Otomatik sertifika yenileme

## 🛠️ Komutlar

### Servisleri Başlatma

```bash
# Tüm servisleri başlat
docker-compose up -d

# Sadece temel servisleri başlat
docker-compose up -d mysql ollama backend frontend nginx
```

### SSL Sertifika İşlemleri

```bash
# Self-signed certificate oluştur
./nginx/ssl-setup.sh

# Production certificate al
./init-letsencrypt.sh -d yourdomain.com -e admin@yourdomain.com

# Sertifikaları yenile
./renew-certs.sh
```

### Log Kontrolü

```bash
# Nginx logları
docker-compose logs nginx

# Backend logları
docker-compose logs backend

# Tüm servis logları
docker-compose logs
```

## 🔒 Güvenlik

### Rate Limiting

- **API Endpoints**: 10 req/s (burst: 20)
- **Frontend**: 50 req/s (burst: 50)
- **Login Endpoints**: 5 req/m

### Security Headers

- `Strict-Transport-Security`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `X-XSS-Protection`
- `Content-Security-Policy`

## 🌐 Erişim URL'leri

- **Frontend**: https://pentorasecbeta.mywire.org
- **API**: https://pentorasecbeta.mywire.org/api
- **Health Check**: https://pentorasecbeta.mywire.org/health
- **phpMyAdmin**: https://pentorasecbeta.mywire.org/phpmyadmin

## 🔄 Otomatik Yenileme

Sertifikaları otomatik yenilemek için crontab'a ekleyin:

```bash
# Her gün saat 12:00'da kontrol et
0 12 * * * /path/to/your/project/renew-certs.sh >> /var/log/certbot-renewal.log 2>&1
```

## 🐛 Sorun Giderme

### SSL Sertifika Sorunları

```bash
# Sertifika durumunu kontrol et
docker-compose exec certbot certbot certificates

# Sertifikaları test et
docker-compose exec certbot certbot renew --dry-run
```

### Nginx Konfigürasyon Testi

```bash
# Konfigürasyonu test et
docker-compose exec nginx nginx -t

# Nginx'i yeniden yükle
docker-compose exec nginx nginx -s reload
```

### Port Çakışması

```bash
# Port kullanımını kontrol et
netstat -tulpn | grep :80
netstat -tulpn | grep :443

# Çakışan servisleri durdur
sudo systemctl stop apache2  # Apache varsa
sudo systemctl stop nginx    # Sistem Nginx'i varsa
```

## 📊 Monitoring

### Health Check Endpoints

- `GET /health` - Backend sağlık durumu
- `GET /api/health` - API sağlık durumu

### Log Monitoring

```bash
# Real-time log takibi
docker-compose logs -f nginx
docker-compose logs -f backend
```

## 🔧 Gelişmiş Konfigürasyon

### Custom Domain

1. `nginx/conf.d/default.conf` dosyasını düzenleyin
2. `your-domain.com` yerine kendi domain'inizi yazın
3. `init-letsencrypt.sh` scriptini yeni domain ile çalıştırın

### Load Balancing

Birden fazla backend instance'ı için upstream konfigürasyonu:

```nginx
upstream backend {
    server pentest_backend_1:8001;
    server pentest_backend_2:8001;
    server pentest_backend_3:8001;
    keepalive 32;
}
```

## 📞 Destek

Sorun yaşarsanız:

1. Log dosyalarını kontrol edin
2. Docker container durumlarını kontrol edin
3. Network bağlantılarını test edin
4. SSL sertifika geçerliliğini kontrol edin
