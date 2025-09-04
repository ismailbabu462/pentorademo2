# Pentest Tools Docker Image

Bu Docker imajı, penetration testing için gerekli tüm araçları içerir.

## İçerilen Araçlar

### Go-based Tools
- **Subfinder** - Subdomain discovery
- **Amass** - Attack surface mapping
- **Nuclei** - Vulnerability scanner
- **ffuf** - Web fuzzer
- **Gobuster** - Directory brute forcer

### System Tools
- **Nmap** - Port scanner
- **Dirb** - Directory scanner
- **Nikto** - Web vulnerability scanner
- **SQLMap** - SQL injection tool
- **Hydra** - Password brute forcer
- **John** - Password cracker
- **Hashcat** - Advanced password recovery
- **Aircrack-ng** - Wireless security tools
- **Wireshark** - Network protocol analyzer
- **Tcpdump** - Network packet analyzer

### Wordlists
- **SecLists** - Comprehensive security testing wordlists
- **Rockyou** - Common password list
- **Common directories** - Web directory enumeration

## Kullanım

### 1. Tools Container'ı Başlatma

```bash
# Sadece tools container'ını başlatmak için
docker-compose --profile tools up -d tools

# Tüm servisleri başlatmak için
docker-compose up -d
```

### 2. Tools Container'ına Bağlanma

```bash
docker exec -it pentest_tools bash
```

### 3. Tool'ları Test Etme

```bash
# Subfinder test
subfinder -d example.com -silent

# Amass test
amass enum -d example.com -passive

# Nmap test
nmap -sV -sC example.com

# Nuclei test
nuclei -u https://example.com -severity critical,high

# ffuf test
ffuf -u https://example.com/FUZZ -w /usr/share/wordlists/common.txt

# Gobuster test
gobuster dir -u https://example.com -w /usr/share/wordlists/common.txt
```

## Docker Compose Entegrasyonu

Tools container'ı backend ile volume üzerinden bağlanır:
- Backend, `/opt/tools` dizinindeki tool'ları kullanır
- Tools container'ı çalışmadığında backend tool'ları bulamaz

## Güvenlik

- Container non-root user (`pentester`) olarak çalışır
- Tools sadece read-only olarak backend'e mount edilir
- Network izolasyonu sağlanır

## Troubleshooting

### Tool Bulunamadı Hatası
```bash
# Tools container'ının çalıştığından emin olun
docker-compose ps tools

# Tools container'ını yeniden başlatın
docker-compose restart tools
```

### Permission Hatası
```bash
# Tools container'ına bağlanıp permissions'ları kontrol edin
docker exec -it pentest_tools ls -la /opt/tools
```

## Geliştirme

Yeni tool eklemek için:
1. `tools/Dockerfile`'a tool'u ekleyin
2. `backend/server.py`'de tool execution fonksiyonunu güncelleyin
3. Container'ı yeniden build edin: `docker-compose build tools`

