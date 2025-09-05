# Linting ve Code Quality Rehberi

Bu proje hem backend (Python) hem de frontend (React/JavaScript) için kapsamlı linting ve code quality araçları ile yapılandırılmıştır.

## Kurulum

### Tüm bağımlılıkları yüklemek için:
```bash
make install
```

### Sadece backend bağımlılıkları:
```bash
make backend-install
```

### Sadece frontend bağımlılıkları:
```bash
make frontend-install
```

## Linting Araçları

### Backend (Python)
- **flake8**: PEP 8 uyumluluğu ve kod kalitesi kontrolü
- **black**: Otomatik kod formatlama
- **isort**: Import sıralama
- **mypy**: Tip kontrolü

### Frontend (React/JavaScript)
- **ESLint**: JavaScript/React kod kalitesi kontrolü
- **Prettier**: Otomatik kod formatlama
- **eslint-plugin-react-hooks**: React hooks kuralları

## Kullanım

### Tüm projeler için linting:
```bash
make lint
```

### Tüm projeler için formatlama:
```bash
make format
```

### Backend için:
```bash
# Linting
make backend-lint

# Formatlama
make backend-format
```

### Frontend için:
```bash
# Linting
make frontend-lint

# Formatlama
make frontend-format
```

## IDE Entegrasyonu

### VS Code için önerilen eklentiler:
- Python: Python, Pylance, Black Formatter
- JavaScript/React: ESLint, Prettier, Auto Rename Tag

### VS Code ayarları (.vscode/settings.json):
```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "eslint.validate": ["javascript", "javascriptreact"],
  "prettier.requireConfig": true
}
```

## Konfigürasyon Dosyaları

- `backend/.flake8`: flake8 ayarları
- `backend/pyproject.toml`: black, isort, mypy ayarları
- `frontend/.eslintrc.js`: ESLint ayarları
- `frontend/.prettierrc`: Prettier ayarları
- `frontend/.prettierignore`: Prettier ignore dosyası

## CI/CD Entegrasyonu

Linting kontrollerini CI/CD pipeline'ınıza eklemek için:

```yaml
# GitHub Actions örneği
- name: Run Linting
  run: make lint

- name: Check Formatting
  run: make format
```

## Sorun Giderme

### Python import hataları:
```bash
cd backend
export PYTHONPATH=$PWD:$PYTHONPATH
```

### Node modules sorunları:
```bash
cd frontend
rm -rf node_modules yarn.lock
yarn install
```

### Cache temizleme:
```bash
make clean
```
