# Zepix Trading Bot v2.0 - Deployment & Maintenance Guide

## Overview

This document provides comprehensive instructions for deploying, monitoring, updating, and maintaining the Zepix Trading Bot v2.0 in production environments.

## Deployment Options

### Option 1: Local Windows Deployment

Best for: Personal use with MT5 terminal on same machine.

**Requirements:**
- Windows 10/11
- MetaTrader 5 installed
- Python 3.10+
- Stable internet connection

**Deployment Steps:**

1. **Clone Repository**
```bash
git clone https://github.com/asggroupsinfo/ZepixTradingBot-new-v13.git
cd ZepixTradingBot-new-v13
```

2. **Setup Environment**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
copy .env.example .env
# Edit .env with your credentials
```

4. **Start MT5 Terminal**
- Open MetaTrader 5
- Login to your trading account
- Keep terminal running

5. **Start Bot**
```bash
# Using batch file
START_BOT.bat

# Or manually
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Option 2: VPS Deployment (Linux + Windows)

Best for: 24/7 operation with remote access.

**Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                     LINUX VPS                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Zepix Trading Bot (FastAPI)                        │   │
│  │  - Webhook receiver                                 │   │
│  │  - Telegram bot                                     │   │
│  │  - Trading logic                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           │ MT5 API                         │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Wine + MT5 Terminal                                │   │
│  │  (or Windows VM with MT5)                           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Linux VPS Setup:**

1. **Update System**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Install Python**
```bash
sudo apt install python3.10 python3.10-venv python3-pip -y
```

3. **Clone and Setup**
```bash
cd /opt
sudo git clone https://github.com/asggroupsinfo/ZepixTradingBot-new-v13.git
cd ZepixTradingBot-new-v13
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Configure Environment**
```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

5. **Setup MT5 via Wine (Optional)**
```bash
# Install Wine
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install wine64 wine32 -y

# Install MT5
wine mt5setup.exe
```

### Option 3: Docker Deployment

Best for: Containerized, reproducible deployments.

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  trading-bot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
      - MT5_LOGIN=${MT5_LOGIN}
      - MT5_PASSWORD=${MT5_PASSWORD}
      - MT5_SERVER=${MT5_SERVER}
    volumes:
      - ./config:/app/config
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

**Deploy with Docker:**
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Process Management

### Using systemd (Linux)

**Create Service File:**
```bash
sudo nano /etc/systemd/system/zepix-bot.service
```

**Service Configuration:**
```ini
[Unit]
Description=Zepix Trading Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/ZepixTradingBot-new-v13
Environment="PATH=/opt/ZepixTradingBot-new-v13/venv/bin"
ExecStart=/opt/ZepixTradingBot-new-v13/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable zepix-bot
sudo systemctl start zepix-bot
sudo systemctl status zepix-bot
```

**Service Commands:**
```bash
# Start
sudo systemctl start zepix-bot

# Stop
sudo systemctl stop zepix-bot

# Restart
sudo systemctl restart zepix-bot

# View logs
sudo journalctl -u zepix-bot -f
```

### Using PM2 (Node.js Process Manager)

**Install PM2:**
```bash
npm install -g pm2
```

**Create ecosystem.config.js:**
```javascript
module.exports = {
  apps: [{
    name: 'zepix-bot',
    script: 'venv/bin/uvicorn',
    args: 'src.main:app --host 0.0.0.0 --port 8000',
    cwd: '/opt/ZepixTradingBot-new-v13',
    interpreter: 'none',
    env: {
      TELEGRAM_TOKEN: 'your_token',
      TELEGRAM_CHAT_ID: 'your_chat_id',
      MT5_LOGIN: 'your_login',
      MT5_PASSWORD: 'your_password',
      MT5_SERVER: 'your_server'
    }
  }]
};
```

**PM2 Commands:**
```bash
# Start
pm2 start ecosystem.config.js

# Stop
pm2 stop zepix-bot

# Restart
pm2 restart zepix-bot

# View logs
pm2 logs zepix-bot

# Monitor
pm2 monit
```

### Using Screen (Simple)

```bash
# Start new screen session
screen -S zepix-bot

# Activate environment and start
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

# Detach: Ctrl+A, then D

# Reattach
screen -r zepix-bot
```

## Reverse Proxy Setup

### Nginx Configuration

**Install Nginx:**
```bash
sudo apt install nginx -y
```

**Create Configuration:**
```bash
sudo nano /etc/nginx/sites-available/zepix-bot
```

**Configuration File:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Enable Site:**
```bash
sudo ln -s /etc/nginx/sites-available/zepix-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

## Monitoring

### Health Check Monitoring

**Simple Health Check Script:**
```bash
#!/bin/bash
# health_check.sh

HEALTH_URL="http://localhost:8000/health"
TELEGRAM_TOKEN="your_token"
CHAT_ID="your_chat_id"

response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $response != "200" ]; then
    message="⚠️ Zepix Bot Health Check Failed! Status: $response"
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
        -d "chat_id=$CHAT_ID" \
        -d "text=$message"
    
    # Attempt restart
    sudo systemctl restart zepix-bot
fi
```

**Add to Crontab:**
```bash
# Run every 5 minutes
*/5 * * * * /opt/ZepixTradingBot-new-v13/scripts/health_check.sh
```

### Log Monitoring

**Log Rotation Configuration:**
```bash
sudo nano /etc/logrotate.d/zepix-bot
```

```
/opt/ZepixTradingBot-new-v13/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload zepix-bot > /dev/null 2>&1 || true
    endscript
}
```

### Resource Monitoring

**Monitor Script:**
```bash
#!/bin/bash
# monitor.sh

# Get process info
PID=$(pgrep -f "uvicorn src.main:app")

if [ -z "$PID" ]; then
    echo "Bot not running!"
    exit 1
fi

# Memory usage
MEM=$(ps -o rss= -p $PID | awk '{print $1/1024 " MB"}')

# CPU usage
CPU=$(ps -o %cpu= -p $PID)

# Disk usage
DISK=$(df -h /opt/ZepixTradingBot-new-v13 | tail -1 | awk '{print $5}')

echo "PID: $PID"
echo "Memory: $MEM"
echo "CPU: $CPU%"
echo "Disk: $DISK"
```

## Backup Procedures

### Database Backup

**Manual Backup:**
```bash
# Create backup directory
mkdir -p /opt/backups/zepix-bot

# Backup database
cp /opt/ZepixTradingBot-new-v13/data/trading_bot.db \
   /opt/backups/zepix-bot/trading_bot_$(date +%Y%m%d_%H%M%S).db
```

**Automated Backup Script:**
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/opt/backups/zepix-bot"
BOT_DIR="/opt/ZepixTradingBot-new-v13"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp $BOT_DIR/data/trading_bot.db $BACKUP_DIR/trading_bot_$DATE.db

# Backup configuration
cp $BOT_DIR/config/config.json $BACKUP_DIR/config_$DATE.json
cp $BOT_DIR/config/timeframe_trends.json $BACKUP_DIR/trends_$DATE.json

# Backup stats
cp $BOT_DIR/data/stats.json $BACKUP_DIR/stats_$DATE.json

# Compress old backups
find $BACKUP_DIR -name "*.db" -mtime +7 -exec gzip {} \;

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Schedule Daily Backup:**
```bash
# Add to crontab
0 0 * * * /opt/ZepixTradingBot-new-v13/scripts/backup.sh
```

### Configuration Backup

```bash
# Backup all configuration
tar -czvf config_backup_$(date +%Y%m%d).tar.gz \
    config/config.json \
    config/timeframe_trends.json \
    .env
```

### Full System Backup

```bash
# Full backup (excluding venv and __pycache__)
tar -czvf zepix_full_backup_$(date +%Y%m%d).tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    /opt/ZepixTradingBot-new-v13
```

## Update Procedures

### Standard Update

```bash
# 1. Stop the bot
sudo systemctl stop zepix-bot

# 2. Backup current state
./scripts/backup.sh

# 3. Pull latest changes
cd /opt/ZepixTradingBot-new-v13
git pull origin main

# 4. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 5. Start the bot
sudo systemctl start zepix-bot

# 6. Verify health
curl http://localhost:8000/health
```

### Rolling Update (Zero Downtime)

```bash
# 1. Clone to new directory
git clone https://github.com/asggroupsinfo/ZepixTradingBot-new-v13.git \
    /opt/ZepixTradingBot-new-v13-new

# 2. Setup new instance
cd /opt/ZepixTradingBot-new-v13-new
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Copy configuration
cp /opt/ZepixTradingBot-new-v13/.env .
cp /opt/ZepixTradingBot-new-v13/config/* config/
cp /opt/ZepixTradingBot-new-v13/data/* data/

# 4. Start new instance on different port
uvicorn src.main:app --host 0.0.0.0 --port 8001 &

# 5. Test new instance
curl http://localhost:8001/health

# 6. Switch nginx to new port
# Edit /etc/nginx/sites-available/zepix-bot
# Change proxy_pass to port 8001
sudo nginx -t && sudo systemctl reload nginx

# 7. Stop old instance
sudo systemctl stop zepix-bot

# 8. Swap directories
mv /opt/ZepixTradingBot-new-v13 /opt/ZepixTradingBot-new-v13-old
mv /opt/ZepixTradingBot-new-v13-new /opt/ZepixTradingBot-new-v13

# 9. Update systemd and restart
sudo systemctl start zepix-bot
```

### Rollback Procedure

```bash
# 1. Stop current bot
sudo systemctl stop zepix-bot

# 2. Restore from backup
mv /opt/ZepixTradingBot-new-v13 /opt/ZepixTradingBot-new-v13-failed
mv /opt/ZepixTradingBot-new-v13-old /opt/ZepixTradingBot-new-v13

# 3. Restore database if needed
cp /opt/backups/zepix-bot/trading_bot_YYYYMMDD.db \
   /opt/ZepixTradingBot-new-v13/data/trading_bot.db

# 4. Start bot
sudo systemctl start zepix-bot
```

## Maintenance Tasks

### Daily Maintenance

1. **Check Health Status**
```bash
curl http://localhost:8000/health
```

2. **Review Logs**
```bash
tail -100 /opt/ZepixTradingBot-new-v13/logs/bot.log | grep -E "(ERROR|WARNING)"
```

3. **Check Risk Status**
- Via Telegram: `/risk_status`

4. **Verify MT5 Connection**
- Via Telegram: `/status`

### Weekly Maintenance

1. **Review Error Patterns**
```bash
grep -i error logs/bot.log | cut -d':' -f4 | sort | uniq -c | sort -rn | head -20
```

2. **Check Disk Space**
```bash
df -h /opt/ZepixTradingBot-new-v13
```

3. **Review Trade Performance**
- Via Telegram: `/performance`

4. **Verify Backups**
```bash
ls -la /opt/backups/zepix-bot/
```

### Monthly Maintenance

1. **Update Dependencies**
```bash
pip list --outdated
pip install --upgrade <package>
```

2. **Review and Optimize Configuration**
- Analyze trading performance
- Adjust risk parameters if needed
- Update SL/TP settings based on market conditions

3. **Clean Old Logs**
```bash
find logs/ -name "*.log.*" -mtime +30 -delete
```

4. **Database Maintenance**
```bash
sqlite3 data/trading_bot.db "VACUUM;"
sqlite3 data/trading_bot.db "ANALYZE;"
```

5. **Security Updates**
```bash
sudo apt update && sudo apt upgrade -y
```

## Disaster Recovery

### Scenario 1: Server Crash

1. Provision new server
2. Install dependencies
3. Clone repository
4. Restore configuration from backup
5. Restore database from backup
6. Start bot
7. Verify operation

### Scenario 2: Database Corruption

1. Stop bot
2. Backup corrupted database (for analysis)
3. Restore from latest backup
4. Start bot
5. Verify data consistency

### Scenario 3: Configuration Lost

1. Stop bot
2. Restore .env from secure storage
3. Restore config.json from backup
4. Restore timeframe_trends.json from backup
5. Start bot

### Scenario 4: MT5 Connection Lost

1. Check MT5 terminal status
2. Verify network connectivity
3. Check credentials
4. Restart MT5 terminal
5. Restart bot if needed

## Security Hardening

### Server Security

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart sshd

# Install fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

### Application Security

1. **Environment Variables**
- Never commit .env to git
- Use strong, unique passwords
- Rotate credentials periodically

2. **File Permissions**
```bash
chmod 600 .env
chmod 644 config/config.json
chmod 700 scripts/*.sh
```

3. **Network Security**
- Use HTTPS with valid SSL certificate
- Restrict webhook access by IP if possible
- Use strong Telegram bot token

## Performance Optimization

### Python Optimization

```bash
# Use production ASGI server
pip install gunicorn

# Run with multiple workers
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_trades_open_time ON trades(open_time);
CREATE INDEX IF NOT EXISTS idx_chains_status ON reentry_chains(status);
```

### Memory Optimization

- Monitor memory usage regularly
- Restart bot weekly to clear memory
- Use log rotation to prevent large log files

## Troubleshooting Deployment Issues

### Issue: Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### Issue: Permission Denied

```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu /opt/ZepixTradingBot-new-v13

# Fix permissions
chmod -R 755 /opt/ZepixTradingBot-new-v13
```

### Issue: Service Won't Start

```bash
# Check service status
sudo systemctl status zepix-bot

# Check logs
sudo journalctl -u zepix-bot -n 100

# Test manually
cd /opt/ZepixTradingBot-new-v13
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Issue: SSL Certificate Expired

```bash
# Renew certificate
sudo certbot renew

# Force renewal
sudo certbot renew --force-renewal
```

## Related Documentation

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Project overview
- [CONFIGURATION_SETUP.md](CONFIGURATION_SETUP.md) - Configuration guide
- [ERROR_HANDLING_TROUBLESHOOTING.md](ERROR_HANDLING_TROUBLESHOOTING.md) - Troubleshooting
- [LOGGING_SYSTEM.md](LOGGING_SYSTEM.md) - Logging details
