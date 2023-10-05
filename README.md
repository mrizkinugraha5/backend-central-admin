# Central AI
# Template Backend
## Panduan Cara Penggunaan

## Install
- pip install flask
- pip install Flask-JWT-Extended
- pip install Flask-Migrate
- pip install python-dotenv
- pip install opencv-python
- pip install mysql-connector-python
- pip install requests
- pip install PyQRCode
- pip install Flask-Cors
- pip install PyPDF2
- pip install reportlab

### 1. Clone project
```bash
  git clone https://gitlab.com/ccentral.ai/template-backend.git app_name
```

### 2. Buat file .env
untuk membuat file .env kamu dapat menduplikatnya dari file app_name/env simpan pada direktori **app_name/.env**, file ini berfungsi sebagai file konfigurasi untuk mengatur port number, environment database, dan lain sebagainya

### 3. Database
#### Setting Database
seluruh struktur tabel database dapat ditulis pada direktori app_name/database/ dokumentasi format penulisannya dapat dilihat dari referensi berikut ini https://docs.sqlalchemy.org/en/14/core/metadata.html 

#### Setup Migrasi Database pada OS Windows
```bash
    set FLASK_APP=run.py
    $env:FLASK_APP = "run.py"
    export FLASK_APP=run.py(linux)
```
```bash
    flask db init
    flask db migrate -m "migrasi database"
    flask db upgrade
    pip install --upgrade Flask(linux)
```
### 4. Jalankan aplikasi
Setelah semua konfigurasi selesai kamu dapat menjalankan aplikasi dengan cara
```bash
  python run.py
```