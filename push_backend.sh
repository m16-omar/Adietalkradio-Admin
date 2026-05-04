#!/bin/bash

# Configuration
SERVER_IP="187.124.218.83"
SERVER_USER="root"
REMOTE_PATH="/var/www/adietalkradio/Adietalkradio-Admin"
VIRTUAL_ENV_PATH="../virtual" # Based on your logs

echo "🚀 Preparing to push AdieTalk Backend to VPS..."

# 1. Add, commit and push local changes to GitHub
git add .
git commit -m "Production deployment update: merged settings and cleaned structure"
git push origin main

echo "✅ Changes pushed to GitHub."

# 2. Remote commands (Pull from GitHub and restart)
ssh ${SERVER_USER}@${SERVER_IP} << 'EOF'
    cd /var/www/adietalkradio
    
    echo "📥 Pulling latest changes from GitHub..."
    git fetch origin
    git reset --hard origin/main
    
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
    
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
    
    echo "🗄️ Running migrations..."
    python3 manage.py migrate
    
    echo "🎨 Copying static files..."
    mkdir -p static_root
    cp -r venv/lib/python3.13/site-packages/unfold/static/unfold static_root/
    cp -r venv/lib/python3.13/site-packages/unfold/static/admin static_root/
    cp -r venv/lib/python3.13/site-packages/django/contrib/admin/static/admin static_root/
    cp -r static/* static_root/ 2>/dev/null || true
    
    echo "🔄 Restarting service..."
    systemctl restart adietalkradio
    
    echo "✅ Server update complete!"
EOF

echo "✨ Backend updated via GitHub successfully!"
