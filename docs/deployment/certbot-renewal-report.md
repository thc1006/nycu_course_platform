# Certbot SSL Certificate Auto-Renewal Configuration Report

## Date: 2025-10-17

## 1. Certbot Installation Status
- **Installed**: ✓ Yes
- **Version**: 4.0.0
- **Location**: /usr/bin/certbot

## 2. Certificate Status
- **Certificate Name**: nymu.com.tw
- **Domains**: nymu.com.tw, www.nymu.com.tw
- **Key Type**: ECDSA
- **Expiry Date**: 2026-01-15 07:44:30+00:00
- **Validity**: VALID (89 days remaining)
- **Certificate Path**: /etc/letsencrypt/live/nymu.com.tw/fullchain.pem
- **Private Key Path**: /etc/letsencrypt/live/nymu.com.tw/privkey.pem

## 3. Systemd Timer Configuration
- **Timer Status**: Active and Enabled
- **Timer File**: /usr/lib/systemd/system/certbot.timer
- **Service File**: /usr/lib/systemd/system/certbot.service

### Timer Schedule
- **Runs**: Twice daily at 00:00 and 12:00 UTC
- **Randomized Delay**: Up to 12 hours (43200 seconds)
- **Next Run**: Sat 2025-10-18 06:06:01 UTC
- **Last Run**: Fri 2025-10-17 12:39:35 UTC (successful)

### Timer Configuration Details
```ini
[Unit]
Description=Run certbot twice daily

[Timer]
OnCalendar=*-*-* 00,12:00:00
RandomizedDelaySec=43200
Persistent=true

[Install]
WantedBy=timers.target
```

### Service Configuration Details
```ini
[Unit]
Description=Certbot
Documentation=file:///usr/share/doc/python-certbot-doc/html/index.html
Documentation=https://certbot.eff.org/docs

[Service]
Type=oneshot
ExecStart=/usr/bin/certbot -q renew --no-random-sleep-on-renew
PrivateTmp=true
```

## 4. Renewal Configuration
- **Renewal File**: /etc/letsencrypt/renewal/nymu.com.tw.conf
- **Authenticator**: nginx
- **Installer**: nginx
- **Renew Before Expiry**: 30 days
- **ACME Server**: https://acme-v02.api.letsencrypt.org/directory

## 5. Renewal Hooks
- **Deploy Hook Created**: /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
- **Purpose**: Automatically reloads nginx after successful certificate renewal
- **Permissions**: Executable (755)

### Hook Script Content
```bash
#!/bin/bash
# Reload nginx after certificate renewal
systemctl reload nginx
```

## 6. Dry-Run Test Results
- **Test Status**: ✓ PASSED
- **Test Output**: All simulated renewals succeeded
- **Certificate Tested**: /etc/letsencrypt/live/nymu.com.tw/fullchain.pem

## 7. Summary
✓ Certbot is properly installed and configured
✓ Systemd timer is active and will run twice daily
✓ Timer has randomized delay to prevent server load spikes
✓ Certificate is valid for 89 days
✓ Dry-run test passed successfully
✓ Nginx reload hook configured for automatic service reload
✓ Automatic renewal will occur 30 days before expiry (around 2025-12-16)

## 8. Files Created/Modified
1. **/etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh** (CREATED)
   - Purpose: Reload nginx after certificate renewal
   - Owner: root
   - Permissions: 755 (rwxr-xr-x)

## 9. Monitoring Commands
- Check timer status: `systemctl status certbot.timer`
- View next run: `systemctl list-timers certbot.timer`
- View service logs: `journalctl -u certbot.service`
- List certificates: `sudo certbot certificates`
- Manual renewal test: `sudo certbot renew --dry-run`

## 10. Additional Notes
- The timer uses a randomized delay (up to 12 hours) to prevent all servers from hitting Let's Encrypt servers simultaneously
- Certificates will be automatically renewed when they have 30 days or less before expiry
- The nginx authenticator/installer means renewals are handled automatically without manual intervention
- The deploy hook ensures nginx uses the new certificates immediately after renewal
