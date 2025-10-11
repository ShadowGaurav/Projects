# Linux System Administration - Complete Guide

## Introduction

System Administration is the practice of managing, maintaining, and configuring computer systems. As a Linux system administrator (and OS creator), you need to understand how Linux systems operate at a fundamental level.

This guide covers everything from init systems to networking, storage, and security.

---

## 1. Init System - systemd

### What is an Init System?

The **init system** is the first process that starts when Linux boots (PID 1). It:
- Initializes the system
- Starts and manages services
- Handles system states (boot, shutdown, reboot)
- Manages dependencies between services

**Modern Linux uses systemd** (replaced older SysVinit and Upstart).

### Why systemd?

**Advantages**:
- Parallel service startup (faster boot)
- Dependency management
- Socket and D-Bus activation
- Unified logging (journald)
- Resource control (cgroups)
- Timer-based activation (replaces cron)

**Components**:
- `systemd` - Main init system
- `systemctl` - Service management
- `journalctl` - Log viewing
- `timedatectl` - Time/date management
- `hostnamectl` - Hostname management
- `localectl` - Locale settings
- `loginctl` - Login/session management

---

### systemd Unit Types

systemd manages different types of "units":

| Unit Type | Extension | Purpose | Example |
|-----------|-----------|---------|---------|
| Service | `.service` | System services/daemons | `ssh.service` |
| Socket | `.socket` | IPC/network sockets | `docker.socket` |
| Device | `.device` | Hardware devices | `dev-sda.device` |
| Mount | `.mount` | Filesystem mount points | `home.mount` |
| Automount | `.automount` | Auto-mount points | `proc-sys-fs-binfmt_misc.automount` |
| Target | `.target` | Group of units | `multi-user.target` |
| Timer | `.timer` | Scheduled tasks | `apt-daily.timer` |
| Path | `.path` | File/directory monitoring | `cups.path` |
| Slice | `.slice` | Resource management | `user.slice` |
| Scope | `.scope` | Externally created processes | `session-1.scope` |

### Service Units

**Location of unit files**:
```
/etc/systemd/system/          # System administrator units (highest priority)
/run/systemd/system/          # Runtime units
/lib/systemd/system/          # Package-provided units
/usr/lib/systemd/system/      # Alternative location
```

**Anatomy of a Service Unit**:

`/etc/systemd/system/myapp.service`:
```ini
[Unit]
Description=My Application Service
Documentation=https://example.com/docs
After=network.target
Wants=network-online.target
Requires=mysql.service

[Service]
Type=simple
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
ExecStartPre=/opt/myapp/pre-start.sh
ExecStart=/opt/myapp/myapp --config /etc/myapp/config.conf
ExecReload=/bin/kill -HUP $MAINPID
ExecStop=/opt/myapp/shutdown.sh
Restart=on-failure
RestartSec=5s
TimeoutStopSec=30s

# Security hardening
PrivateTmp=yes
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/myapp /var/log/myapp

# Resource limits
MemoryLimit=512M
CPUQuota=50%

# Environment
Environment="NODE_ENV=production"
EnvironmentFile=/etc/myapp/environment

[Install]
WantedBy=multi-user.target
```

**Section Breakdown**:

#### **[Unit] Section**

| Directive | Purpose | Example |
|-----------|---------|---------|
| `Description` | Human-readable description | `Description=Web Server` |
| `Documentation` | Documentation URLs | `Documentation=man:httpd(8)` |
| `After` | Start after these units | `After=network.target` |
| `Before` | Start before these units | `Before=shutdown.target` |
| `Requires` | Hard dependency (fails if missing) | `Requires=mysql.service` |
| `Wants` | Soft dependency (optional) | `Wants=redis.service` |
| `Conflicts` | Cannot run with these units | `Conflicts=apache2.service` |
| `PartOf` | Stopped when parent stops | `PartOf=myapp.service` |
| `BindsTo` | Like Requires + stop together | `BindsTo=myapp.service` |

#### **[Service] Section**

| Directive | Purpose | Values |
|-----------|---------|--------|
| `Type` | Service type | `simple`, `forking`, `oneshot`, `dbus`, `notify`, `idle` |
| `ExecStart` | Command to start service | `/usr/bin/myapp` |
| `ExecStartPre` | Command before start | `/bin/check-config` |
| `ExecStartPost` | Command after start | `/bin/notify-started` |
| `ExecReload` | Command to reload config | `/bin/kill -HUP $MAINPID` |
| `ExecStop` | Command to stop service | `/bin/myapp-stop` |
| `ExecStopPost` | Command after stop | `/bin/cleanup` |
| `Restart` | Restart policy | `no`, `always`, `on-failure`, `on-abnormal` |
| `RestartSec` | Time before restart | `5s`, `1min` |
| `User` | Run as user | `www-data` |
| `Group` | Run as group | `www-data` |
| `WorkingDirectory` | Working directory | `/opt/myapp` |
| `Environment` | Environment variables | `"VAR=value"` |
| `EnvironmentFile` | File with env vars | `/etc/myapp/env` |
| `PIDFile` | PID file location | `/var/run/myapp.pid` |

**Service Types Explained**:

- **`simple`** - Default. Process started is main process (doesn't fork)
- **`forking`** - Process forks and parent exits (traditional daemon)
- **`oneshot`** - Process exits before starting next units (scripts)
- **`dbus`** - Service is ready when D-Bus name appears
- **`notify`** - Service sends notification when ready
- **`idle`** - Delay execution until all jobs finished

#### **[Install] Section**

| Directive | Purpose | Example |
|-----------|---------|---------|
| `WantedBy` | Targets that want this unit | `WantedBy=multi-user.target` |
| `RequiredBy` | Targets that require this unit | `RequiredBy=graphical.target` |
| `Alias` | Alternative names | `Alias=myapp.service` |
| `Also` | Also enable these units | `Also=myapp-worker.service` |

---

### systemctl - Service Management

#### **Basic Service Control**

```bash
# Start a service
sudo systemctl start myapp.service

# Stop a service
sudo systemctl stop myapp.service

# Restart a service
sudo systemctl restart myapp.service

# Reload configuration without restart
sudo systemctl reload myapp.service

# Reload or restart if reload not available
sudo systemctl reload-or-restart myapp.service

# Check if service is running
systemctl is-active myapp.service

# Check if service is enabled
systemctl is-enabled myapp.service
```

#### **Enable/Disable Services**

```bash
# Enable service (start at boot)
sudo systemctl enable myapp.service

# Enable and start immediately
sudo systemctl enable --now myapp.service

# Disable service (don't start at boot)
sudo systemctl disable myapp.service

# Disable and stop immediately
sudo systemctl disable --now myapp.service

# Mask service (completely disable, can't be started)
sudo systemctl mask myapp.service

# Unmask service
sudo systemctl unmask myapp.service
```

#### **Service Status and Information**

```bash
# Show detailed status
systemctl status myapp.service

# Show service properties
systemctl show myapp.service

# Show specific property
systemctl show myapp.service -p MainPID

# Show service file content
systemctl cat myapp.service

# Show dependencies
systemctl list-dependencies myapp.service

# Show reverse dependencies (what depends on this)
systemctl list-dependencies --reverse myapp.service
```

#### **Listing Services**

```bash
# List all units
systemctl list-units

# List all services
systemctl list-units --type=service

# List all services (including inactive)
systemctl list-units --type=service --all

# List failed services
systemctl --failed

# List enabled services
systemctl list-unit-files --state=enabled

# List running services
systemctl list-units --type=service --state=running
```

#### **Working with Unit Files**

```bash
# Edit service file (creates override in /etc/systemd/system/)
sudo systemctl edit myapp.service

# Edit full file (not recommended, use override instead)
sudo systemctl edit --full myapp.service

# Reload systemd configuration after manual edits
sudo systemctl daemon-reload

# Reset failed state
sudo systemctl reset-failed myapp.service
```

---

### System Targets (Runlevels)

**Targets** are groups of units that represent system states.

| Target | SysVinit Equivalent | Purpose |
|--------|---------------------|---------|
| `poweroff.target` | runlevel 0 | Shutdown |
| `rescue.target` | runlevel 1 | Single-user mode |
| `multi-user.target` | runlevel 3 | Multi-user, no GUI |
| `graphical.target` | runlevel 5 | Multi-user with GUI |
| `reboot.target` | runlevel 6 | Reboot |
| `emergency.target` | emergency | Emergency shell |

**Managing Targets**:

```bash
# Show current target
systemctl get-default

# Set default target
sudo systemctl set-default multi-user.target
sudo systemctl set-default graphical.target

# Switch to target (without reboot)
sudo systemctl isolate multi-user.target
sudo systemctl isolate graphical.target

# List all targets
systemctl list-units --type=target

# Show dependencies of target
systemctl list-dependencies multi-user.target
```

**System State Commands**:

```bash
# Reboot
sudo systemctl reboot

# Shutdown
sudo systemctl poweroff

# Suspend (sleep)
sudo systemctl suspend

# Hibernate
sudo systemctl hibernate

# Hybrid sleep (suspend + hibernate)
sudo systemctl hybrid-sleep

# Halt (stop but don't power off)
sudo systemctl halt
```

---

### Timer Units (Replacing Cron)

**Timers** schedule tasks, similar to cron but more powerful.

**Example Timer**: `/etc/systemd/system/backup.timer`
```ini
[Unit]
Description=Daily Backup Timer
Requires=backup.service

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 02:00:00
Persistent=true
AccuracySec=1h

[Install]
WantedBy=timers.target
```

**Corresponding Service**: `/etc/systemd/system/backup.service`
```ini
[Unit]
Description=Backup Service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
User=backup
```

**Timer Directives**:

| Directive | Purpose | Example |
|-----------|---------|---------|
| `OnBootSec` | After boot | `OnBootSec=15min` |
| `OnStartupSec` | After systemd start | `OnStartupSec=10min` |
| `OnUnitActiveSec` | After last activation | `OnUnitActiveSec=1h` |
| `OnUnitInactiveSec` | After last deactivation | `OnUnitInactiveSec=30min` |
| `OnCalendar` | Calendar time | `OnCalendar=Mon *-*-* 00:00:00` |
| `Persistent` | Run if missed while off | `Persistent=true` |
| `AccuracySec` | Accuracy window | `AccuracySec=1min` |

**Calendar Syntax Examples**:

```
*-*-* *:*:*              # Every second
*-*-* 00:00:00           # Daily at midnight
Mon *-*-* 00:00:00       # Every Monday
Mon..Fri *-*-* 09:00:00  # Weekdays at 9 AM
*-*-01 00:00:00          # First day of month
hourly                   # Every hour
daily                    # Every day
weekly                   # Every week
monthly                  # Every month
```

**Managing Timers**:

```bash
# Enable and start timer
sudo systemctl enable --now backup.timer

# List all timers
systemctl list-timers

# List all timers (including inactive)
systemctl list-timers --all

# Show timer status
systemctl status backup.timer

# Trigger timer manually
sudo systemctl start backup.service
```

---

### journald - System Logging

**journald** is systemd's logging system, replacing traditional syslog.

#### **Viewing Logs**

```bash
# View all logs
journalctl

# View logs from current boot
journalctl -b

# View logs from previous boot
journalctl -b -1

# View logs since specific time
journalctl --since "2025-10-10 10:00:00"
journalctl --since "1 hour ago"
journalctl --since yesterday
journalctl --since today

# View logs until specific time
journalctl --until "2025-10-10 12:00:00"

# Combine since and until
journalctl --since "2025-10-10 10:00" --until "2025-10-10 12:00"

# Follow logs (like tail -f)
journalctl -f

# Last N lines
journalctl -n 50

# Show kernel messages only
journalctl -k
```

#### **Filtering Logs**

```bash
# Service logs
journalctl -u myapp.service
journalctl -u myapp.service -f

# Multiple services
journalctl -u nginx.service -u php-fpm.service

# Priority filtering (error and above)
journalctl -p err
journalctl -p warning

# Priority levels: emerg, alert, crit, err, warning, notice, info, debug

# By process ID
journalctl _PID=1234

# By user
journalctl _UID=1000

# By executable
journalctl /usr/bin/myapp

# Combine filters
journalctl -u myapp.service -p err --since today
```

#### **Log Output Formats**

```bash
# Short format (default)
journalctl -o short

# Verbose (all fields)
journalctl -o verbose

# JSON format
journalctl -o json

# Pretty JSON
journalctl -o json-pretty

# Export format (binary)
journalctl -o export

# Cat format (only message)
journalctl -o cat
```

#### **Log Management**

```bash
# Disk usage
journalctl --disk-usage

# Verify journal files
journalctl --verify

# Vacuum logs by size
sudo journalctl --vacuum-size=100M

# Vacuum logs by time
sudo journalctl --vacuum-time=2weeks

# Rotate logs
sudo systemctl kill --signal=SIGUSR2 systemd-journald
```

#### **Configuration**

**File**: `/etc/systemd/journald.conf`

```ini
[Journal]
# Storage location
Storage=persistent         # or auto, volatile, none

# Size limits
SystemMaxUse=500M         # Max disk usage
SystemMaxFileSize=50M     # Max per file
RuntimeMaxUse=100M        # Max in /run

# Retention
MaxRetentionSec=1month    # Keep for 1 month
MaxFileSec=1week          # Rotate weekly

# Forwarding
ForwardToSyslog=no
ForwardToKMsg=no
ForwardToConsole=no

# Rate limiting
RateLimitIntervalSec=30s
RateLimitBurst=10000
```

After changes:
```bash
sudo systemctl restart systemd-journald
```

---

## 2. Networking

### Network Configuration in Debian

Debian uses several network management systems:
- **`ifupdown`** - Traditional (legacy)
- **NetworkManager** - Desktop systems
- **systemd-networkd** - Modern systemd-based

### ifupdown (Traditional Method)

**Configuration**: `/etc/network/interfaces`

```bash
# Loopback interface
auto lo
iface lo inet loopback

# DHCP configuration
auto eth0
iface eth0 inet dhcp

# Static IP configuration
auto eth1
iface eth1 inet static
    address 192.168.1.100
    netmask 255.255.255.0
    gateway 192.168.1.1
    dns-nameservers 8.8.8.8 8.8.4.4
    dns-search example.com

# Wireless (requires wpasupplicant)
auto wlan0
iface wlan0 inet dhcp
    wpa-ssid MyNetwork
    wpa-psk MyPassword

# Bridge
auto br0
iface br0 inet static
    address 192.168.1.10
    netmask 255.255.255.0
    bridge_ports eth0 eth1
    bridge_stp off
    bridge_fd 0

# VLAN
auto eth0.100
iface eth0.100 inet static
    address 192.168.100.1
    netmask 255.255.255.0
    vlan-raw-device eth0
```

**Commands**:

```bash
# Bring interface up
sudo ifup eth0

# Bring interface down
sudo ifdown eth0

# Restart networking
sudo systemctl restart networking

# Show interface status
ip addr show
ip link show
```

### NetworkManager (Desktop)

**GUI**: `nm-applet` (system tray icon)
**TUI**: `nmtui` (text interface)
**CLI**: `nmcli` (command line)

#### **nmcli Commands**

```bash
# Show all connections
nmcli connection show

# Show active connections
nmcli connection show --active

# Show devices
nmcli device status

# Show detailed device info
nmcli device show eth0

# Connect to network
nmcli connection up "Connection Name"

# Disconnect
nmcli connection down "Connection Name"

# Create new connection (DHCP)
nmcli connection add type ethernet con-name "My Connection" ifname eth0

# Create static IP connection
nmcli connection add type ethernet con-name "Static" ifname eth0 \
    ip4 192.168.1.100/24 gw4 192.168.1.1

# Modify connection
nmcli connection modify "Connection Name" ipv4.addresses 192.168.1.150/24
nmcli connection modify "Connection Name" ipv4.gateway 192.168.1.1
nmcli connection modify "Connection Name" ipv4.dns "8.8.8.8 8.8.4.4"
nmcli connection modify "Connection Name" ipv4.method manual

# WiFi
nmcli device wifi list
nmcli device wifi connect "SSID" password "password"

# Delete connection
nmcli connection delete "Connection Name"

# Reload connections
nmcli connection reload
```

### systemd-networkd

**Enable systemd-networkd**:
```bash
sudo systemctl enable systemd-networkd
sudo systemctl start systemd-networkd
```

**Configuration**: `/etc/systemd/network/`

**DHCP Example**: `/etc/systemd/network/20-wired.network`
```ini
[Match]
Name=eth0

[Network]
DHCP=yes
```

**Static IP Example**: `/etc/systemd/network/20-wired.network`
```ini
[Match]
Name=eth0

[Network]
Address=192.168.1.100/24
Gateway=192.168.1.1
DNS=8.8.8.8
DNS=8.8.4.4
```

**Bridge Example**: `/etc/systemd/network/25-bridge.netdev`
```ini
[NetDev]
Name=br0
Kind=bridge
```

`/etc/systemd/network/25-bridge.network`
```ini
[Match]
Name=br0

[Network]
Address=192.168.1.10/24
Gateway=192.168.1.1
```

**Apply changes**:
```bash
sudo systemctl restart systemd-networkd
```

---

### DNS Configuration

#### **/etc/resolv.conf**

DNS resolver configuration:

```bash
# Traditional (static)
nameserver 8.8.8.8
nameserver 8.8.4.4
search example.com
```

**Modern systems** use `systemd-resolved`:

```bash
# Enable systemd-resolved
sudo systemctl enable systemd-resolved
sudo systemctl start systemd-resolved

# Link resolv.conf to systemd-resolved
sudo ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

# Check DNS settings
resolvectl status

# Query DNS
resolvectl query example.com

# Flush DNS cache
resolvectl flush-caches
```

#### **/etc/hosts**

Static hostname to IP mapping:

```bash
127.0.0.1       localhost
127.0.1.1       yourhostname
192.168.1.100   server.example.com server

# IPv6
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
```

#### **/etc/hostname**

System hostname:

```bash
yourhostname
```

**Change hostname**:
```bash
# Temporarily
sudo hostname newhostname

# Permanently
sudo hostnamectl set-hostname newhostname

# Verify
hostnamectl
```

---

### Network Tools

#### **ip command** (Modern, replaces ifconfig/route)

```bash
# Show all interfaces
ip addr show
ip a

# Show specific interface
ip addr show eth0

# Add IP address
sudo ip addr add 192.168.1.100/24 dev eth0

# Delete IP address
sudo ip addr del 192.168.1.100/24 dev eth0

# Bring interface up/down
sudo ip link set eth0 up
sudo ip link set eth0 down

# Show routing table
ip route show
ip r

# Add route
sudo ip route add 192.168.2.0/24 via 192.168.1.1

# Add default gateway
sudo ip route add default via 192.168.1.1

# Delete route
sudo ip route del 192.168.2.0/24

# Show ARP table
ip neigh show

# Show statistics
ip -s link show eth0
```

#### **Legacy Tools**

```bash
# ifconfig (deprecated, use ip instead)
ifconfig
ifconfig eth0
sudo ifconfig eth0 192.168.1.100 netmask 255.255.255.0

# route (deprecated, use ip route)
route -n
sudo route add default gw 192.168.1.1

# arp (deprecated, use ip neigh)
arp -a
```

#### **Network Testing**

```bash
# Test connectivity
ping 8.8.8.8
ping -c 4 google.com

# Trace route
traceroute google.com
traceroute -n 8.8.8.8

# MTR (better traceroute)
mtr google.com

# DNS lookup
nslookup google.com
dig google.com
host google.com

# Test port connectivity
nc -zv google.com 80
telnet google.com 80

# Download test
wget https://example.com
curl https://example.com

# Speed test (install speedtest-cli)
speedtest-cli
```

#### **Network Monitoring**

```bash
# Active connections
netstat -tuln        # TCP/UDP listening
netstat -tulpn       # With process names (requires root)
ss -tuln             # Modern replacement for netstat
ss -tulpn

# Show all connections
ss -a

# Show TCP connections
ss -t

# Show listening sockets
ss -l

# Bandwidth monitoring
sudo iftop           # Real-time bandwidth by connection
sudo nethogs         # Bandwidth by process
sudo bmon            # Interface monitoring
nload eth0           # Bandwidth usage

# Packet capture
sudo tcpdump -i eth0
sudo tcpdump -i eth0 port 80
sudo tcpdump -i eth0 -w capture.pcap
```

---

### Firewall - iptables/nftables

#### **UFW (Uncomplicated Firewall)** - Easiest

```bash
# Install
sudo apt install ufw

# Enable/disable
sudo ufw enable
sudo ufw disable

# Status
sudo ufw status
sudo ufw status verbose
sudo ufw status numbered

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow services
sudo ufw allow ssh
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3000:3999/tcp    # Port range

# Allow from specific IP
sudo ufw allow from 192.168.1.100

# Allow from subnet
sudo ufw allow from 192.168.1.0/24

# Allow specific IP to specific port
sudo ufw allow from 192.168.1.100 to any port 22

# Deny
sudo ufw deny 23/tcp

# Delete rule
sudo ufw delete allow 80/tcp
sudo ufw delete 2              # By number

# Reload
sudo ufw reload

# Reset (delete all rules)
sudo ufw reset
```

#### **iptables** - More Control

**View rules**:
```bash
# List all rules
sudo iptables -L
sudo iptables -L -v -n

# List with line numbers
sudo iptables -L --line-numbers

# List specific chain
sudo iptables -L INPUT
```

**Basic rules**:
```bash
# Allow SSH
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow from specific IP
sudo iptables -A INPUT -s 192.168.1.100 -j ACCEPT

# Allow established connections
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow loopback
sudo iptables -A INPUT -i lo -j ACCEPT

# Drop everything else
sudo iptables -A INPUT -j DROP

# Delete rule
sudo iptables -D INPUT 3      # By line number
sudo iptables -D INPUT -p tcp --dport 80 -j ACCEPT  # By specification
```

**Save rules**:
```bash
# Debian/Ubuntu
sudo iptables-save > /etc/iptables/rules.v4
sudo ip6tables-save > /etc/iptables/rules.v6

# Or use iptables-persistent
sudo apt install iptables-persistent
sudo netfilter-persistent save
```

#### **nftables** - Modern Replacement

```bash
# Install
sudo apt install nftables

# Enable
sudo systemctl enable nftables
sudo systemctl start nftables

# List rules
sudo nft list ruleset

# Configuration file
sudo nano /etc/nftables.conf
```

**Example nftables.conf**:
```
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        
        # Allow loopback
        iif lo accept
        
        # Allow established/related
        ct state established,related accept
        
        # Allow SSH
        tcp dport 22 accept
        
        # Allow HTTP/HTTPS
        tcp dport {80, 443} accept
        
        # Allow ping
        icmp type echo-request accept
    }
    
    chain forward {
        type filter hook forward priority 0; policy drop;
    }
    
    chain output {
        type filter hook output priority 0; policy accept;
    }
}
```

**Apply**:
```bash
sudo nft -f /etc/nftables.conf
sudo systemctl reload nftables
```

---

## 3. Storage Management

### Disk Partitioning

#### **fdisk** - MBR partitions

```bash
# List disks
sudo fdisk -l

# Partition disk
sudo fdisk /dev/sda

# Commands in fdisk:
# m - help
# p - print partition table
# n - new partition
# d - delete partition
# t - change partition type
# w - write changes and exit
# q - quit without saving
```

#### **gdisk** - GPT partitions

```bash
# Partition disk (GPT)
sudo gdisk /dev/sda

# Similar commands to fdisk
```

#### **parted** - Both MBR and GPT

```bash
# Interactive mode
sudo parted /dev/sda

# Commands:
# print - show partitions
# mklabel gpt - create GPT table
# mklabel msdos - create MBR table
# mkpart primary ext4 0% 50% - create partition
# rm 1 - delete partition 1
# quit - exit

# Non-interactive
sudo parted /dev/sda mklabel gpt
sudo parted /dev/sda mkpart primary ext4 0% 100%
```

### Viewing Disk Information

```bash
# List block devices
lsblk
lsblk -f        # With filesystem info

# Show disk usage
df -h
df -h /home

# Show directory size
du -sh /var/log
du -h --max-depth=1 /var

# Disk I/O statistics
iostat
sudo iotop      # Per-process I/O

# Detailed disk info
sudo hdparm -I /dev/sda
sudo smartctl -a /dev/sda  # SMART info (install smartmontools)
```

### Filesystems

#### **Creating Filesystems**

```bash
# ext4 (most common)
sudo mkfs.ext4 /dev/sda1
sudo mkfs.ext4 -L mylabel /dev/sda1  # With label

# ext3
sudo mkfs.ext3 /dev/sda1

# xfs
sudo mkfs.xfs /dev/sda1

# btrfs
sudo mkfs.btrfs /dev/sda1

# FAT32
sudo mkfs.vfat -F 32 /dev/sda1

# exFAT
sudo mkfs.exfat /dev/sda1

# NTFS
sudo mkfs.ntfs /dev/sda1
```

#### **Checking and Repairing Filesystems**

```bash
# Check filesystem (unmount first!)
sudo umount /dev/sda1
sudo fsck /dev/sda1

# Force check
sudo fsck -f /dev/sda1

# Auto-repair
sudo fsck -y /dev/sda1

# ext4 specific
sudo e2fsck /dev/sda1
sudo e2fsck -f -y /dev/sda1

# Check and repair XFS
sudo xfs_repair /dev/sda1
```

#### **Filesystem Labels and UUIDs**

```bash
# Show UUIDs
sudo blkid

# Set label (ext4)
sudo e2label /dev/sda1 "mylabel"

# Set label (XFS)
sudo xfs_admin -L "mylabel" /dev/sda1

# Set label (FAT)
sudo fatlabel /dev/sda1 "mylabel"
```

### Mounting Filesystems

#### **Temporary Mounting**

```bash
# Mount filesystem
sudo mount /dev/sda1 /mnt

# Mount with options
sudo mount -o ro /dev/sda1 /mnt              # Read-only
sudo mount -o rw,noexec /dev/sda1 /mnt       # Read-write, no execution
sudo mount -o uid=1000,gid=1000 /dev/sda1 /mnt  # Set owner

# Mount by UUID
sudo mount UUID=xxxxx-xxxxx /mnt

# Mount by label
sudo mount LABEL=mylabel /mnt

# Mount ISO file
sudo mount -o loop image.iso /mnt

# Mount network share (NFS)
sudo mount -t nfs server:/share /mnt

# Mount network share (CIFS/Samba)
sudo mount -t cifs //server/share /mnt -o username=user,password=pass

# Unmount
sudo umount /mnt
sudo umount /dev/sda1

# Force unmount
sudo umount -f /mnt

# Lazy unmount (detach now, cleanup when no longer busy)
sudo umount -l /mnt

# Show what's using the mount
lsof /mnt
fuser -m /mnt
```

#### **Permanent Mounting - /etc/fstab**

**Format**: `device mountpoint fstype options dump pass`

`/etc/fstab` example:
```bash
# <device>                          <mount>         <type>  <options>           <dump> <pass>
UUID=xxxxx-xxxxx-xxxxx              /               ext4    errors=remount-ro   0      1
UUID=yyyyy-yyyyy-yyyyy              /home           ext4    defaults            0      2
UUID=zzzzz-zzzzz-zzzzz              none            swap    sw                  0      0
/dev/sdb1                           /mnt/backup     ext4    defaults            0      2
LABEL=myusb                         /mnt/usb        vfat    noauto,user         0      0
//server/share                      /mnt/share      cifs    credentials=/root/.smbcreds  0  0
server:/export                      /mnt/nfs        nfs     defaults            0      0
/path/to/image.iso                  /mnt/iso        iso9660 loop,ro             0      0
tmpfs                               /tmp            tmpfs   defaults,size=2G    0      0
```

**Options**:

| Option | Description |
|--------|-------------|
| `defaults` | rw,suid,dev,exec,auto,nouser,async |
| `auto` | Mount at boot |
| `noauto` | Don't mount at boot (manual) |
| `user` | Allow non-root users to mount |
| `nouser` | Only root can mount |
| `ro` | Read-only |
| `rw` | Read-write |
| `exec` | Allow execution of binaries |
| `noexec` | Prevent execution of binaries |
| `suid` | Allow SUID/SGID bits |
| `nosuid` | Ignore SUID/SGID bits |
| `dev` | Interpret block/character devices |
| `nodev` | Don't interpret devices |
| `sync` | Synchronous I/O |
| `async` | Asynchronous I/O |
| `nofail` | Don't fail boot if device missing |
| `x-systemd.automount` | Automount on access |

**Test fstab**:
```bash
# Test without actually mounting
sudo mount -a --fake

# Mount all filesystems in fstab
sudo mount -a

# Remount all
sudo mount -a -o remount
```

### LVM (Logical Volume Manager)

LVM provides flexible disk management with the ability to resize partitions dynamically.

**Hierarchy**: Physical Volumes (PV) → Volume Groups (VG) → Logical Volumes (LV)

```
Disk 1 (/dev/sda)     Disk 2 (/dev/sdb)
     |                      |
   PV (/dev/sda1)      PV (/dev/sdb1)
     |                      |
     └──────────┬───────────┘
                |
           VG (vg0)
                |
        ┌───────┼────────┐
        |       |        |
    LV (root) (home) (swap)
        |       |        |
       /      /home    [SWAP]
```

#### **Creating LVM**

```bash
# Install LVM tools
sudo apt install lvm2

# Create Physical Volume
sudo pvcreate /dev/sda1
sudo pvcreate /dev/sdb1

# Show physical volumes
sudo pvs
sudo pvdisplay

# Create Volume Group
sudo vgcreate vg0 /dev/sda1 /dev/sdb1

# Show volume groups
sudo vgs
sudo vgdisplay

# Create Logical Volume
sudo lvcreate -L 20G -n root vg0        # Fixed size
sudo lvcreate -L 50G -n home vg0
sudo lvcreate -l 100%FREE -n data vg0   # Use remaining space

# Show logical volumes
sudo lvs
sudo lvdisplay

# Create filesystem
sudo mkfs.ext4 /dev/vg0/root
sudo mkfs.ext4 /dev/vg0/home

# Mount
sudo mount /dev/vg0/root /mnt
```

#### **Resizing LVM**

```bash
# Extend Logical Volume
sudo lvextend -L +10G /dev/vg0/home      # Add 10GB
sudo lvextend -l +100%FREE /dev/vg0/home # Use all free space

# Resize filesystem (ext4)
sudo resize2fs /dev/vg0/home

# Or do both at once
sudo lvextend -L +10G -r /dev/vg0/home

# Reduce Logical Volume (CAREFUL! Can lose data)
# Must resize filesystem first
sudo resize2fs /dev/vg0/home 40G
sudo lvreduce -L 40G /dev/vg0/home

# Extend Volume Group (add new disk)
sudo pvcreate /dev/sdc1
sudo vgextend vg0 /dev/sdc1
```

#### **LVM Snapshots**

```bash
# Create snapshot
sudo lvcreate -L 5G -s -n home-snap /dev/vg0/home

# Mount snapshot
sudo mount /dev/vg0/home-snap /mnt/snapshot

# Restore from snapshot (CAREFUL!)
sudo umount /mnt/home
sudo lvconvert --merge /dev/vg0/home-snap

# Remove snapshot
sudo lvremove /dev/vg0/home-snap
```

#### **Removing LVM**

```bash
# Remove Logical Volume
sudo lvremove /dev/vg0/home

# Remove Volume Group
sudo vgremove vg0

# Remove Physical Volume
sudo pvremove /dev/sda1
```

### RAID (Redundant Array of Independent Disks)

**mdadm** - Software RAID on Linux

**RAID Levels**:

| Level | Name | Description | Min Disks | Usable Space |
|-------|------|-------------|-----------|--------------|
| RAID 0 | Striping | Performance, no redundancy | 2 | 100% |
| RAID 1 | Mirroring | Full redundancy | 2 | 50% |
| RAID 5 | Striping with parity | Good balance | 3 | (n-1)/n |
| RAID 6 | Double parity | Better redundancy | 4 | (n-2)/n |
| RAID 10 | Mirror + Stripe | Best performance + redundancy | 4 | 50% |

#### **Creating RAID**

```bash
# Install mdadm
sudo apt install mdadm

# Create RAID 1 (mirror)
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc

# Create RAID 5
sudo mdadm --create /dev/md0 --level=5 --raid-devices=3 /dev/sdb /dev/sdc /dev/sdd

# Create RAID 10
sudo mdadm --create /dev/md0 --level=10 --raid-devices=4 /dev/sdb /dev/sdc /dev/sdd /dev/sde

# Check RAID status
cat /proc/mdstat
sudo mdadm --detail /dev/md0

# Create filesystem on RAID
sudo mkfs.ext4 /dev/md0

# Mount
sudo mount /dev/md0 /mnt
```

#### **Managing RAID**

```bash
# Add spare disk
sudo mdadm --add /dev/md0 /dev/sdf

# Remove disk
sudo mdadm --fail /dev/md0 /dev/sdc
sudo mdadm --remove /dev/md0 /dev/sdc

# Replace failed disk
sudo mdadm --add /dev/md0 /dev/sdg  # Add new disk
# RAID will automatically rebuild

# Stop RAID
sudo mdadm --stop /dev/md0

# Assemble RAID
sudo mdadm --assemble /dev/md0 /dev/sdb /dev/sdc

# Save configuration
sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf
sudo update-initramfs -u
```

### Swap Space

**Swap** is disk space used as virtual memory when RAM is full.

#### **Swap Partition**

```bash
# Create partition with type 82 (Linux swap)
sudo fdisk /dev/sda

# Format as swap
sudo mkswap /dev/sda2

# Enable swap
sudo swapon /dev/sda2

# Make permanent (/etc/fstab)
UUID=xxxxx-xxxxx  none  swap  sw  0  0

# Check swap
swapon --show
free -h
```

#### **Swap File**

```bash
# Create swap file
sudo fallocate -l 4G /swapfile
# Or
sudo dd if=/dev/zero of=/swapfile bs=1G count=4

# Set permissions
sudo chmod 600 /swapfile

# Make swap
sudo mkswap /swapfile

# Enable
sudo swapon /swapfile

# Make permanent (/etc/fstab)
/swapfile  none  swap  sw  0  0

# Verify
swapon --show
```

#### **Swap Management**

```bash
# Disable swap
sudo swapoff /swapfile
sudo swapoff -a  # All swap

# Change swappiness (how aggressively to use swap)
# 0 = avoid swap, 100 = aggressive
cat /proc/sys/vm/swappiness
sudo sysctl vm.swappiness=10

# Make permanent (/etc/sysctl.conf)
vm.swappiness=10

# Remove swap file
sudo swapoff /swapfile
sudo rm /swapfile
# Remove from /etc/fstab
```

---

## 4. User and Permission Management

### User Management

#### **Creating Users**

```bash
# Add user (interactive)
sudo adduser username

# Add user (non-interactive)
sudo useradd -m -s /bin/bash username
sudo passwd username

# Add user with specific UID/GID
sudo useradd -u 1500 -g 1500 -m username

# Add user to additional groups
sudo useradd -m -G sudo,www-data username

# Create system user (no home, no shell)
sudo useradd -r -s /usr/sbin/nologin servicename
```

#### **Modifying Users**

```bash
# Change user password
sudo passwd username

# Change user shell
sudo chsh -s /bin/zsh username

# Change user home directory
sudo usermod -d /new/home -m username

# Add user to group
sudo usermod -aG groupname username
sudo adduser username groupname  # Debian-specific

# Remove user from group
sudo gpasswd -d username groupname

# Change user UID
sudo usermod -u 2000 username

# Lock user account
sudo usermod -L username
sudo passwd -l username

# Unlock user account
sudo usermod -U username
sudo passwd -u username

# Set account expiry
sudo usermod -e 2025-12-31 username

# Disable account (no shell)
sudo usermod -s /usr/sbin/nologin username
```

#### **Deleting Users**

```bash
# Delete user (keep home directory)
sudo userdel username

# Delete user and home directory
sudo userdel -r username

# Force delete (even if logged in)
sudo userdel -f username
```

#### **User Information**

```bash
# List all users
cat /etc/passwd
getent passwd

# Show user info
id username
finger username
groups username

# Show logged in users
who
w
last
lastlog

# Show user's groups
groups username
id -Gn username
```

### Group Management

```bash
# Create group
sudo groupadd groupname

# Create group with specific GID
sudo groupadd -g 1500 groupname

# Modify group
sudo groupmod -g 2000 groupname      # Change GID
sudo groupmod -n newname oldname     # Rename

# Delete group
sudo groupdel groupname

# List all groups
cat /etc/group
getent group

# Show group members
getent group groupname
```

### File Permissions

#### **Understanding Permissions**

```bash
ls -l filename
# Output: -rwxr-xr--  1 user group 1234 Oct 10 10:00 filename
#         │││││││││
#         │││││││└└─ Other permissions (r--)
#         │││││└─┴── Group permissions (r-x)
#         │││└─┴──── User permissions (rwx)
#         ││└──────── Special permissions
#         │└───────── Number of hard links
#         └────────── File type (- = file, d = directory, l = link)
```

**Permission meanings**:
- **r (read)**: Read file contents / List directory contents
- **w (write)**: Modify file / Create/delete files in directory
- **x (execute)**: Execute file / Enter directory

**Numeric representation**:
- r = 4, w = 2, x = 1
- rwx = 7, rw- = 6, r-x = 5, r-- = 4

#### **Changing Permissions - chmod**

```bash
# Symbolic mode
chmod u+x file          # Add execute for user
chmod g-w file          # Remove write for group
chmod o+r file          # Add read for others
chmod a+x file          # Add execute for all
chmod u=rwx,g=rx,o=r file  # Set exact permissions

# Numeric mode
chmod 755 file          # rwxr-xr-x
chmod 644 file          # rw-r--r--
chmod 600 file          # rw-------
chmod 777 file          # rwxrwxrwx (dangerous!)
chmod 700 directory     # rwx------ (common for directories)

# Recursive
chmod -R 755 directory

# Only directories
find /path -type d -exec chmod 755 {} \;

# Only files
find /path -type f -exec chmod 644 {} \;
```

#### **Changing Ownership - chown**

```bash
# Change owner
sudo chown user file

# Change owner and group
sudo chown user:group file

# Change only group
sudo chown :group file
sudo chgrp group file

# Recursive
sudo chown -R user:group directory

# Change ownership to match another file
sudo chown --reference=file1 file2
```

#### **Special Permissions**

**SUID (Set User ID)** - File executes with owner's permissions
```bash
chmod u+s file
chmod 4755 file
# Example: /usr/bin/passwd (runs as root)
```

**SGID (Set Group ID)** - File executes with group's permissions / New files inherit directory group
```bash
chmod g+s file
chmod 2755 file
# Useful for shared directories
```

**Sticky Bit** - Only owner can delete files (common for /tmp)
```bash
chmod +t directory
chmod 1777 directory
# Example: /tmp
```

**Find files with special permissions**:
```bash
# Find SUID files
find / -perm -4000 -type f 2>/dev/null

# Find SGID files
find / -perm -2000 -type f 2>/dev/null

# Find world-writable directories with sticky bit
find / -type d -perm -1000 2>/dev/null
```

### Access Control Lists (ACLs)

More fine-grained permissions than traditional Unix permissions.

```bash
# Install ACL tools
sudo apt install acl

# Check if filesystem supports ACL
mount | grep acl

# Enable ACL on filesystem (if needed)
sudo tune2fs -o acl /dev/sda1

# View ACL
getfacl file

# Set ACL - give user read/write
setfacl -m u:username:rw file

# Set ACL - give group read
setfacl -m g:groupname:r file

# Remove specific ACL
setfacl -x u:username file

# Remove all ACLs
setfacl -b file

# Set default ACL (for new files in directory)
setfacl -d -m u:username:rw directory

# Recursive
setfacl -R -m u:username:rw directory

# Copy ACL from one file to another
getfacl file1 | setfacl --set-file=- file2
```

### sudo Configuration

**sudo** allows users to run commands as root (or other users).

#### **/etc/sudoers**

**NEVER edit directly!** Always use `visudo`:
```bash
sudo visudo
```

**Basic syntax**:
```
user    hosts=(run_as) commands
```

**Examples**:
```bash
# Allow user to run all commands as root
username ALL=(ALL:ALL) ALL

# Allow user without password
username ALL=(ALL) NOPASSWD: ALL

# Allow group
%groupname ALL=(ALL:ALL) ALL

# Allow specific commands
username ALL=(ALL) /usr/bin/apt, /usr/bin/systemctl

# Allow user to run as specific user
username ALL=(otheruser) ALL

# Allow only on specific host
username hostname=(ALL) ALL

# Alias for command groups
Cmnd_Alias NETWORKING = /sbin/route, /sbin/ifconfig, /bin/ping
username ALL = NETWORKING
```

**sudo commands**:
```bash
# Run command as root
sudo command

# Run as specific user
sudo -u username command

# Run with user's environment
sudo -E command

# Start shell as root
sudo -i
sudo -s

# Edit file (uses $EDITOR or $VISUAL)
sudoedit /etc/config

# List sudo privileges
sudo -l

# Validate sudo (extend timeout)
sudo -v

# Kill sudo session
sudo -k
```

---

## 5. Process Management

### Understanding Processes

Every running program is a process with:
- **PID** (Process ID) - Unique identifier
- **PPID** (Parent Process ID) - Parent process
- **UID/GID** - User/group running it
- **State** - Running, sleeping, zombie, etc.
- **Priority** - CPU scheduling priority
- **Memory** - RAM usage

### Viewing Processes

#### **ps - Process Status**

```bash
# Show current user's processes
ps

# Show all processes
ps aux
ps -ef

# Show process tree
ps auxf
ps -ejH

# Show processes for specific user
ps -u username

# Show process by PID
ps -p 1234

# Show process by name
ps -C nginx

# Custom format
ps -eo pid,ppid,user,cmd,%mem,%cpu --sort=-%mem
```

**ps aux output explained**:
```
USER  PID %CPU %MEM    VSZ   RSS TTY   STAT START   TIME COMMAND
root    1  0.0  0.1 169820 11964 ?     Ss   Oct10   0:05 /sbin/init
```

**STAT codes**:
- R = Running
- S = Sleeping (interruptible)
- D = Sleeping (uninterruptible, usually I/O)
- T = Stopped
- Z = Zombie
- < = High priority
- N = Low priority
- s = Session leader
- + = Foreground process group

#### **top - Real-time View**

```bash
# Basic top
top

# Sort by memory
top -o %MEM

# Sort by CPU
top -o %CPU

# Show specific user
top -u username

# Batch mode (non-interactive)
top -b -n 1

# While in top:
# k - kill process
# r - renice process
# M - sort by memory
# P - sort by CPU
# 1 - show individual CPUs
# q - quit
```

#### **htop - Better top**

```bash
# Install
sudo apt install htop

# Run
htop

# Features:
# - Mouse support
# - Tree view (F5)
# - Filter (F4)
# - Search (F3)
# - Kill (F9)
# - Nice (F7/F8)
```

#### **Other Process Tools**

```bash
# pgrep - Find process by name
pgrep nginx
pgrep -u username

# pidof - Find PID by name
pidof nginx

# pstree - Process tree
pstree
pstree -p  # Show PIDs

# List open files for process
lsof -p 1234

# List processes using a file
lsof /var/log/syslog

# List processes using a port
lsof -i :80
lsof -i TCP:22
```

### Managing Processes

#### **Starting Processes**

```bash
# Run in foreground
command

# Run in background
command &

# Run with low priority (nice)
nice -n 10 command

# Run with high priority (requires root)
nice -n -10 command
```

#### **Process Control**

```bash
# Suspend current process (Ctrl+Z)
Ctrl+Z

# List background jobs
jobs

# Bring job to foreground
fg %1
fg

# Send job to background
bg %1

# Disown job (keep running after logout)
disown %1
disown -a  # All jobs
```

#### **nohup - Run After Logout**

```bash
# Run command immune to hangups
nohup command &

# Output goes to nohup.out
nohup command > output.log 2>&1 &
```

#### **screen - Terminal Multiplexer**

```bash
# Install
sudo apt install screen

# Start screen
screen

# Detach: Ctrl+A, then D

# List sessions
screen -ls

# Reattach
screen -r
screen -r session_id

# Create named session
screen -S mysession

# Kill session
screen -X -S mysession quit
```

#### **tmux - Better Terminal Multiplexer**

```bash
# Install
sudo apt install tmux

# Start
tmux

# Detach: Ctrl+B, then D

# List sessions
tmux ls

# Attach
tmux attach
tmux attach -t 0

# New session
tmux new -s mysession

# Kill session
tmux kill-session -t mysession

# Split panes:
# Ctrl+B, then % (vertical)
# Ctrl+B, then " (horizontal)
# Ctrl+B, arrow keys (navigate)
```

### Signals and Killing Processes

**Common signals**:

| Signal | Number | Description | Can catch? |
|--------|--------|-------------|------------|
| SIGHUP | 1 | Hangup (reload config) | Yes |
| SIGINT | 2 | Interrupt (Ctrl+C) | Yes |
| SIGQUIT | 3 | Quit (core dump) | Yes |
| SIGKILL | 9 | Kill (cannot be caught) | NO |
| SIGTERM | 15 | Terminate (graceful) | Yes |
| SIGSTOP | 19 | Stop (cannot be caught) | NO |
| SIGCONT | 18 | Continue | Yes |

#### **kill Command**

```bash
# Send SIGTERM (graceful termination)
kill 1234
kill -15 1234
kill -TERM 1234

# Send SIGKILL (force kill)
kill -9 1234
kill -KILL 1234

# Send SIGHUP (reload)
kill -1 1234
kill -HUP 1234

# Kill all processes with name
killall nginx
killall -9 nginx

# Kill processes matching pattern
pkill nginx
pkill -9 -u username
```

### Process Priority (nice/renice)

**Nice values**: -20 (highest priority) to 19 (lowest priority)

```bash
# Start with specific nice value
nice -n 10 command

# Change priority of running process
renice -n 5 -p 1234

# Change priority for all processes of user
renice -n 10 -u username

# View nice values
ps -eo pid,nice,cmd
```

### System Load and Performance

```bash
# Show system load average
uptime
# Output: 10:00:00 up 5 days, 12:34, 3 users, load average: 0.15, 0.20, 0.18
# Load average: 1 min, 5 min, 15 min

# CPU info
lscpu
cat /proc/cpuinfo

# Memory info
free -h
cat /proc/meminfo

# Disk I/O
iostat
iostat -x 1  # Extended, update every second

# Show top CPU consumers
ps aux --sort=-%cpu | head

# Show top memory consumers
ps aux --sort=-%mem | head

# System activity report
sar
sar -u  # CPU
sar -r  # Memory
sar -d  # Disk
```

---

## 6. System Logging

### journald (covered earlier)

See journald section in Init System.

### Traditional Syslog

**rsyslog** - Traditional logging daemon

**Configuration**: `/etc/rsyslog.conf` and `/etc/rsyslog.d/`

```bash
# Facility.Priority  Destination
*.info               /var/log/messages
auth,authpriv.*      /var/log/auth.log
kern.*               /var/log/kern.log
mail.*               /var/log/mail.log
*.emerg              :omusrmsg:*
```

**Facilities**: auth, authpriv, cron, daemon, kern, mail, user, local0-local7

**Priorities**: emerg, alert, crit, err, warning, notice, info, debug

### Log Rotation - logrotate

**Configuration**: `/etc/logrotate.conf` and `/etc/logrotate.d/`

**Example**: `/etc/logrotate.d/myapp`
```
/var/log/myapp/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 myapp myapp
    sharedscripts
    postrotate
        systemctl reload myapp > /dev/null 2>&1 || true
    endscript
}
```

**Options**:
- `daily`, `weekly`, `monthly` - Rotation frequency
- `rotate 7` - Keep 7 old logs
- `compress` - Gzip old logs
- `delaycompress` - Don't compress most recent
- `missingok` - Don't error if log missing
- `notifempty` - Don't rotate if empty
- `create mode user group` - Create new log file
- `postrotate/endscript` - Commands after rotation

**Test logrotate**:
```bash
# Dry run
sudo logrotate -d /etc/logrotate.conf

# Force rotation
sudo logrotate -f /etc/logrotate.conf
```

---

## 7. System Monitoring

### Performance Monitoring Tools

```bash
# vmstat - Virtual memory statistics
vmstat 1  # Update every second

# iotop - I/O by process
sudo iotop

# iftop - Network bandwidth by connection
sudo iftop

# nethogs - Network bandwidth by process
sudo nethogs

# dstat - Versatile resource statistics
dstat
dstat -cdn  # CPU, disk, network

# glances - All-in-one monitoring
sudo apt install glances
glances

# nmon - Performance monitoring
sudo apt install nmon
nmon
```

### System Information

```bash
# System information
uname -a                  # Kernel info
lsb_release -a            # Distribution info
hostnamectl              # Hostname and OS info
timedatectl              # Time and date info

# Hardware information
lshw                     # Detailed hardware
lshw -short
lscpu                    # CPU info
lsmem                    # Memory info
lsblk                    # Block devices
lspci                    # PCI devices
lsusb                    # USB devices
lsscsi                   # SCSI devices
dmidecode                # DMI/SMBIOS info

# Network hardware
lspci | grep -i network
lsusb | grep -i wireless
ip link show
```

---

## 8. Backup and Recovery

### Backup Tools

#### **tar - Archive Tool**

```bash
# Create archive
tar -czf backup.tar.gz /path/to/backup

# Create with verbose output
tar -cvzf backup.tar.gz /path/to/backup

# Extract
tar -xzf backup.tar.gz

# Extract to specific directory
tar -xzf backup.tar.gz -C /destination

# List contents
tar -tzf backup.tar.gz

# Exclude files
tar -czf backup.tar.gz --exclude='*.log' /path

# Incremental backup
tar -czf full.tar.gz --listed-incremental=backup.snar /path
tar -czf incr.tar.gz --listed-incremental=backup.snar /path
```

#### **rsync - Efficient File Sync**

```bash
# Local sync
rsync -avz /source/ /destination/

# Remote sync (push)
rsync -avz /source/ user@remote:/destination/

# Remote sync (pull)
rsync -avz user@remote:/source/ /destination/

# With progress
rsync -avz --progress /source/ /destination/

# Exclude files
rsync -avz --exclude='*.log' /source/ /destination/

# Delete files in destination not in source
rsync -avz --delete /source/ /destination/

# Dry run
rsync -avz --dry-run /source/ /destination/

# Preserve hard links
rsync -avzH /source/ /destination/

# Bandwidth limit
rsync -avz --bwlimit=1000 /source/ /destination/
```

#### **dd - Disk Clone**

```bash
# Clone entire disk
sudo dd if=/dev/sda of=/dev/sdb bs=64K status=progress

# Create disk image
sudo dd if=/dev/sda of=/path/to/image.img bs=64K status=progress

# Restore from image
sudo dd if=/path/to/image.img of=/dev/sda bs=64K status=progress

# Backup MBR
sudo dd if=/dev/sda of=mbr-backup bs=512 count=1

# Restore MBR
sudo dd if=mbr-backup of=/dev/sda bs=512 count=1
```

#### **Automated Backup Scripts**

**Example backup script**:
```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/backup"
SOURCE="/home /etc /var/www"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="backup-$DATE.tar.gz"
LOG_FILE="/var/log/backup.log"
RETENTION_DAYS=30

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

# Create backup
echo "$(date): Starting backup" >> "$LOG_FILE"
if tar -czf "$BACKUP_DIR/$BACKUP_FILE" $SOURCE 2>> "$LOG_FILE"; then
    echo "$(date): Backup completed successfully" >> "$LOG_FILE"
else
    echo "$(date): Backup failed" >> "$LOG_FILE"
    exit 1
fi

# Remove old backups
find "$BACKUP_DIR" -name "backup-*.tar.gz" -mtime +$RETENTION_DAYS -delete
echo "$(date): Old backups cleaned" >> "$LOG_FILE"

# Optional: Upload to remote server
# rsync -avz "$BACKUP_DIR/$BACKUP_FILE" user@remote:/backups/
```

**Make executable and schedule**:
```bash
sudo chmod +x /usr/local/bin/backup.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
0 2 * * * /usr/local/bin/backup.sh

# Or create systemd timer (see Timer Units section)
```

---

## 9. Security Hardening

### SSH Security

**Configuration**: `/etc/ssh/sshd_config`

```bash
# Disable root login
PermitRootLogin no

# Use key-based authentication only
PasswordAuthentication no
PubkeyAuthentication yes

# Change default port
Port 2222

# Limit users
AllowUsers user1 user2
AllowGroups sshusers

# Disable empty passwords
PermitEmptyPasswords no

# Timeout idle sessions
ClientAliveInterval 300
ClientAliveCountMax 2

# Disable X11 forwarding if not needed
X11Forwarding no

# Use strong ciphers only
Ciphers aes256-ctr,aes192-ctr,aes128-ctr
MACs hmac-sha2-512,hmac-sha2-256

# Apply changes
sudo systemctl restart sshd
```

**SSH Key Management**:

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Copy key to server
ssh-copy-id user@server

# Manual copy
cat ~/.ssh/id_ed25519.pub | ssh user@server "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# Set correct permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

### Fail2ban - Intrusion Prevention

**Install and configure**:

```bash
# Install
sudo apt install fail2ban

# Copy default config
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Edit configuration
sudo nano /etc/fail2ban/jail.local
```

**Example configuration**:
```ini
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5
destemail = admin@example.com
sendername = Fail2Ban
action = %(action_mwl)s

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
bantime = 24h
```

**Manage fail2ban**:
```bash
# Status
sudo fail2ban-client status

# Status for specific jail
sudo fail2ban-client status sshd

# Unban IP
sudo fail2ban-client set sshd unbanip 192.168.1.100

# Ban IP manually
sudo fail2ban-client set sshd banip 192.168.1.100

# Reload
sudo fail2ban-client reload
```

### AppArmor - Mandatory Access Control

**AppArmor** provides additional security by restricting programs' capabilities.

```bash
# Check status
sudo aa-status

# Enable profile
sudo aa-enforce /etc/apparmor.d/usr.bin.program

# Set to complain mode (log only)
sudo aa-complain /etc/apparmor.d/usr.bin.program

# Disable profile
sudo aa-disable /etc/apparmor.d/usr.bin.program

# Reload all profiles
sudo systemctl reload apparmor
```

### Security Auditing

#### **System File Integrity - AIDE**

```bash
# Install
sudo apt install aide

# Initialize database
sudo aideinit

# Move database
sudo mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# Check for changes
sudo aide --check

# Update database
sudo aide --update
sudo mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
```

#### **Port Scanning**

```bash
# Check open ports locally
sudo ss -tuln
sudo netstat -tuln

# Scan with nmap
nmap localhost
nmap -sV 192.168.1.100    # Version detection
nmap -A 192.168.1.100     # Aggressive scan

# Check specific port
nc -zv localhost 80
```

#### **Security Updates**

```bash
# Check for security updates
sudo apt update
apt list --upgradable

# Install security updates only
sudo unattended-upgrade

# Configure automatic updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

**Configuration**: `/etc/apt/apt.conf.d/50unattended-upgrades`

```
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
```

---

## 10. System Boot Process

### Understanding Boot Sequence

1. **BIOS/UEFI** - Hardware initialization, POST
2. **Boot Loader (GRUB)** - Loads kernel
3. **Kernel** - Hardware detection, loads initramfs
4. **initramfs** - Temporary root filesystem
5. **systemd (PID 1)** - Init system takes over
6. **Targets** - System reaches target (multi-user, graphical)

### GRUB Bootloader

**Configuration**: `/etc/default/grub`

```bash
# Default boot entry
GRUB_DEFAULT=0

# Timeout before auto-boot
GRUB_TIMEOUT=5

# Hide GRUB menu (show on Shift/Esc)
GRUB_TIMEOUT_STYLE=hidden

# Kernel parameters
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX=""

# Resolution
GRUB_GFXMODE=1920x1080

# Disable graphics
# GRUB_TERMINAL=console

# Apply changes
sudo update-grub
```

**Common kernel parameters**:
- `quiet` - Suppress most boot messages
- `splash` - Show splash screen
- `nomodeset` - Disable KMS (for graphics issues)
- `acpi=off` - Disable ACPI
- `single` or `1` - Boot to single-user mode
- `systemd.unit=rescue.target` - Boot to rescue mode
- `init=/bin/bash` - Emergency shell

**GRUB commands**:

```bash
# Reinstall GRUB
sudo grub-install /dev/sda

# Update GRUB configuration
sudo update-grub

# List boot entries
grep menuentry /boot/grub/grub.cfg

# Edit GRUB at boot:
# Press 'e' at GRUB menu
# Edit kernel parameters
# Press Ctrl+X to boot
```

### initramfs

**initramfs** (initial RAM filesystem) contains drivers and tools needed to mount the real root filesystem.

```bash
# Update initramfs
sudo update-initramfs -u

# Create new initramfs
sudo update-initramfs -c -k $(uname -r)

# Rebuild all
sudo update-initramfs -u -k all

# List contents
lsinitramfs /boot/initrd.img-$(uname -r)

# Extract initramfs
mkdir /tmp/initramfs
cd /tmp/initramfs
gunzip -c /boot/initrd.img-$(uname -r) | cpio -idmv
```

### Boot Analysis

```bash
# Show boot time
systemd-analyze

# Show service startup times
systemd-analyze blame

# Show critical chain
systemd-analyze critical-chain

# Plot boot process (creates SVG)
systemd-analyze plot > boot.svg

# Verify system
systemd-analyze verify

# View boot log
journalctl -b
journalctl -b -1  # Previous boot

# Kernel messages
dmesg
dmesg | less
dmesg -T  # Human-readable timestamps
```

---

## 11. Kernel Management

### Viewing Kernel Information

```bash
# Current kernel version
uname -r

# Detailed kernel info
uname -a

# Kernel messages
dmesg

# Kernel configuration
cat /boot/config-$(uname -r)

# Kernel command line
cat /proc/cmdline
```

### Kernel Modules

**Kernel modules** are pieces of code loaded into the kernel on demand (drivers, filesystems, etc.).

```bash
# List loaded modules
lsmod

# Module information
modinfo module_name

# Load module
sudo modprobe module_name

# Unload module
sudo modprobe -r module_name
sudo rmmod module_name

# Load module with parameters
sudo modprobe module_name param=value

# Blacklist module (prevent loading)
echo "blacklist module_name" | sudo tee /etc/modprobe.d/blacklist-module.conf

# Load module at boot
echo "module_name" | sudo tee -a /etc/modules

# Module parameters at boot
echo "options module_name param=value" | sudo tee /etc/modprobe.d/module.conf
```

### Installing/Removing Kernels

```bash
# List installed kernels
dpkg -l | grep linux-image

# Install new kernel
sudo apt install linux-image-amd64

# Install specific version
sudo apt install linux-image-5.10.0-20-amd64

# Remove old kernel
sudo apt remove linux-image-5.4.0-old-amd64
sudo apt autoremove

# Keep current and one previous
# Edit: /etc/apt/apt.conf.d/01autoremove-kernels
```

### Kernel Parameters (sysctl)

**Runtime kernel parameters** can be modified without reboot.

```bash
# View all parameters
sysctl -a

# View specific parameter
sysctl net.ipv4.ip_forward

# Set parameter temporarily
sudo sysctl -w net.ipv4.ip_forward=1

# Make permanent (/etc/sysctl.conf or /etc/sysctl.d/)
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-custom.conf

# Reload sysctl configuration
sudo sysctl -p
sudo sysctl --system
```

**Common parameters**:

```bash
# Network
net.ipv4.ip_forward=1                    # Enable IP forwarding
net.ipv4.tcp_syncookies=1               # SYN flood protection
net.ipv4.conf.all.accept_source_route=0 # Disable source routing
net.ipv4.conf.all.rp_filter=1          # Reverse path filtering
net.ipv4.icmp_echo_ignore_all=0        # Respond to ping

# Kernel
kernel.panic=10                         # Reboot after panic
kernel.sysrq=1                          # Enable SysRq keys
kernel.core_uses_pid=1                  # Append PID to core dumps

# Virtual Memory
vm.swappiness=10                        # Swap usage tendency
vm.dirty_ratio=15                       # Dirty page threshold
vm.dirty_background_ratio=5             # Background write threshold

# File System
fs.file-max=2097152                     # Max open files system-wide
fs.inotify.max_user_watches=524288     # inotify watches limit

# Security
kernel.randomize_va_space=2             # ASLR
kernel.kptr_restrict=1                  # Hide kernel pointers
```

---

## 12. Time and Date Management

### System Time

```bash
# Show current time
date

# Show hardware clock
sudo hwclock

# Set system time from hardware clock
sudo hwclock --hctosys

# Set hardware clock from system time
sudo hwclock --systohc

# Set date manually
sudo date -s "2025-10-11 10:30:00"
```

### timedatectl (systemd)

```bash
# Show time status
timedatectl

# Set timezone
timedatectl list-timezones
sudo timedatectl set-timezone America/New_York

# Set time
sudo timedatectl set-time "2025-10-11 10:30:00"

# Set date
sudo timedatectl set-time "2025-10-11"

# Enable/disable NTP
sudo timedatectl set-ntp true
sudo timedatectl set-ntp false

# Set hardware clock to UTC
sudo timedatectl set-local-rtc 0
```

### NTP (Network Time Protocol)

#### **systemd-timesyncd** (Default)

```bash
# Status
timedatectl timesync-status

# Configuration: /etc/systemd/timesyncd.conf
[Time]
NTP=0.debian.pool.ntp.org 1.debian.pool.ntp.org
FallbackNTP=ntp.ubuntu.com

# Restart
sudo systemctl restart systemd-timesyncd
```

#### **chrony** (Alternative, more accurate)

```bash
# Install
sudo apt install chrony

# Configuration: /etc/chrony/chrony.conf
server 0.debian.pool.ntp.org iburst
server 1.debian.pool.ntp.org iburst

# Status
chronyc tracking
chronyc sources

# Force sync
sudo chronyc makestep

# Restart
sudo systemctl restart chrony
```

---

## 13. Locale and Internationalization

### Locales

```bash
# Show current locale
locale

# List available locales
locale -a

# Generate locale
sudo locale-gen en_US.UTF-8

# Set system locale
sudo localectl set-locale LANG=en_US.UTF-8

# Update locale (Debian)
sudo dpkg-reconfigure locales
```

**Configuration**: `/etc/default/locale`

```bash
LANG=en_US.UTF-8
LC_ALL=en_US.UTF-8
```

### Keyboard Layout

```bash
# Show keyboard layout
localectl status

# List keyboard layouts
localectl list-keymaps

# Set keyboard layout
sudo localectl set-keymap us

# Set X11 keyboard
sudo localectl set-x11-keymap us

# Temporary change (console)
sudo loadkeys us

# Reconfigure (Debian)
sudo dpkg-reconfigure keyboard-configuration
```

---

## 14. System Performance Tuning

### CPU Governor

Control CPU frequency scaling:

```bash
# Show current governor
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Available governors
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors
# Typical: performance, powersave, ondemand, conservative, schedutil

# Set governor (temporary)
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Install cpufrequtils
sudo apt install cpufrequtils

# Set governor (persistent)
sudo systemctl disable ondemand
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
sudo systemctl restart cpufrequtils
```

### I/O Scheduler

Control disk I/O scheduling:

```bash
# Show current scheduler
cat /sys/block/sda/queue/scheduler

# Available: none, mq-deadline, kyber, bfq

# Set scheduler (temporary)
echo "mq-deadline" | sudo tee /sys/block/sda/queue/scheduler

# Set at boot (kernel parameter)
# Add to GRUB_CMDLINE_LINUX: elevator=mq-deadline
```

### Transparent Huge Pages

```bash
# Check status
cat /sys/kernel/mm/transparent_hugepage/enabled

# Disable (some databases prefer this)
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled

# Make permanent (add to /etc/rc.local or systemd service)
```

### Resource Limits

**Configuration**: `/etc/security/limits.conf`

```bash
# Format: <domain> <type> <item> <value>

# Open files
*               soft    nofile          65536
*               hard    nofile          65536

# Processes
*               soft    nproc           8192
*               hard    nproc           8192

# Core dumps
*               soft    core            unlimited

# Memory
@developers     hard    as              2097152
```

**System-wide limits**:
```bash
# View limits
ulimit -a

# Set open files limit
ulimit -n 65536

# Set process limit
ulimit -u 8192

# Systemd service limits (in unit file)
[Service]
LimitNOFILE=65536
LimitNPROC=8192
```

---

## 15. Cron - Scheduled Tasks

### cron Syntax

```
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday = 0)
# │ │ │ │ │
# * * * * * command to execute
```

**Special strings**:
- `@reboot` - Run at startup
- `@yearly` - Run once a year (0 0 1 1 *)
- `@annually` - Same as @yearly
- `@monthly` - Run once a month (0 0 1 * *)
- `@weekly` - Run once a week (0 0 * * 0)
- `@daily` - Run once a day (0 0 * * *)
- `@midnight` - Same as @daily
- `@hourly` - Run once an hour (0 * * * *)

### Managing cron

```bash
# Edit user crontab
crontab -e

# List user crontab
crontab -l

# Remove user crontab
crontab -r

# Edit other user's crontab (as root)
sudo crontab -u username -e

# System-wide cron
sudo nano /etc/crontab
```

**Example crontab**:
```bash
# Run backup daily at 2 AM
0 2 * * * /usr/local/bin/backup.sh

# Run every 15 minutes
*/15 * * * * /path/to/script.sh

# Run Monday-Friday at 9 AM
0 9 * * 1-5 /path/to/script.sh

# Run on first day of month
0 0 1 * * /path/to/script.sh

# Multiple times
0 0,12 * * * /path/to/script.sh  # Midnight and noon
0 9-17 * * * /path/to/script.sh  # Every hour 9 AM - 5 PM

# With environment variables
MAILTO=admin@example.com
PATH=/usr/local/bin:/usr/bin:/bin
0 2 * * * /path/to/backup.sh
```

**Cron directories** (Debian):
```bash
/etc/cron.daily/      # Daily jobs
/etc/cron.hourly/     # Hourly jobs
/etc/cron.weekly/     # Weekly jobs
/etc/cron.monthly/    # Monthly jobs
/etc/cron.d/          # System cron files
```

**Logs**:
```bash
# View cron logs
grep CRON /var/log/syslog
journalctl -u cron
```

---

## 16. Practical System Admin Tasks

### System Information Script

```bash
#!/bin/bash

echo "=== System Information ==="
echo "Hostname: $(hostname)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Kernel: $(uname -r)"
echo "Uptime: $(uptime -p)"
echo ""

echo "=== CPU Information ==="
lscpu | grep "Model name"
lscpu | grep "CPU(s):"
echo ""

echo "=== Memory Information ==="
free -h
echo ""

echo "=== Disk Usage ==="
df -h | grep -v tmpfs
echo ""

echo "=== Network Information ==="
ip -4 addr show | grep inet | grep -v 127.0.0.1
echo ""

echo "=== Top 5 CPU Processes ==="
ps aux --sort=-%cpu | head -6
echo ""

echo "=== Top 5 Memory Processes ==="
ps aux --sort=-%mem | head -6
echo ""

echo "=== Failed Services ==="
systemctl --failed
```

### User Creation Script

```bash
#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 <username> <fullname>"
    exit 1
fi

USERNAME=$1
FULLNAME=$2

# Create user
useradd -m -c "$FULLNAME" -s /bin/bash "$USERNAME"

# Set password
passwd "$USERNAME"

# Add to sudo group
usermod -aG sudo "$USERNAME"

echo "User $USERNAME created successfully"
```

### Disk Space Alert Script

```bash
#!/bin/bash

THRESHOLD=80
EMAIL="admin@example.com"

df -H | grep -vE '^Filesystem|tmpfs|cdrom' | awk '{ print $5 " " $1 }' | while read output;
do
    usage=$(echo $output | awk '{ print $1}' | sed 's/%//g')
    partition=$(echo $output | awk '{ print $2 }')
    
    if [ $usage -ge $THRESHOLD ]; then
        echo "Disk space alert: $partition is at ${usage}% usage" | \
        mail -s "Disk Space Alert on $(hostname)" $EMAIL
    fi
done
```

---

## 17. Troubleshooting Common Issues

### System Won't Boot

1. **Boot to recovery mode**
   - Select "Advanced options" in GRUB
   - Choose "recovery mode"

2. **Check disk errors**
   ```bash
   sudo fsck /dev/sda1
   ```

3. **Fix GRUB**
   ```bash
   sudo grub-install /dev/sda
   sudo update-grub
   ```

4. **Check kernel panic**
   ```bash
   dmesg | grep -i "panic"
   ```

### High CPU Usage

```bash
# Find process
top
htop
ps aux --sort=-%cpu | head

# Kill process
kill -15 PID
kill -9 PID  # Force

# Check what's running
systemctl list-units --type=service --state=running
```

### High Memory Usage

```bash
# Check memory
free -h
ps aux --sort=-%mem | head

# Check for memory leaks
top (press M to sort by memory)

# Clear cache (usually not needed)
sync
sudo sysctl vm.drop_caches=3
```

### Network Issues

```bash
# Check interfaces
ip addr show
ip link show

# Check connectivity
ping 8.8.8.8
ping google.com

# Check DNS
cat /etc/resolv.conf
dig google.com

# Check routes
ip route show

# Restart networking
sudo systemctl restart networking
sudo systemctl restart NetworkManager

# Check firewall
sudo ufw status
sudo iptables -L
```

### Disk Full

```bash
# Find large files
du -sh /* | sort -h
du -sh /var/* | sort -h

# Find large directories
du -h --max-depth=1 / | sort -h

# Clean package cache
sudo apt clean
sudo apt autoclean

# Clean old logs
sudo journalctl --vacuum-time=7d
sudo find /var/log -name "*.log" -mtime +30 -delete

# Find deleted files still held open
lsof | grep deleted
```

### Service Won't Start

```bash
# Check status
systemctl status service.service

# Check logs
journalctl -u service.service -n 50
journalctl -u service.service -f

# Check configuration
systemctl cat service.service

# Reload systemd
sudo systemctl daemon-reload

# Reset failed state
sudo systemctl reset-failed service.service
```

---

## 18. Best Practices for Your Custom OS

### System Administration

1. **Documentation** - Document all custom configurations
2. **Backups** - Automate regular backups
3. **Updates** - Keep system updated (security)
4. **Monitoring** - Set up system monitoring
5. **Logging** - Centralize and rotate logs
6. **Security** - Follow security hardening guidelines
7. **Testing** - Test in VMs before production

### For Your OS Distribution

1. **Default Services** - Choose which services enable by default
2. **Security Defaults** - UFW enabled, fail2ban configured
3. **Update Policy** - Automatic security updates
4. **System Tools** - Include useful admin tools
5. **Documentation** - System administration guide
6. **Scripts** - Provide useful admin scripts
7. **Monitoring** - Pre-configured monitoring tools

---

## Quick Reference - Essential Commands

### System Info
```bash
uname -a                  # System information
hostnamectl              # Hostname and OS
lsb_release -a           # Distribution info
df -h                    # Disk space
free -h                  # Memory usage
uptime                   # System uptime
```

### Services
```bash
systemctl status NAME    # Service status
systemctl start NAME     # Start service
systemctl stop NAME      # Stop service
systemctl restart NAME   # Restart service
systemctl enable NAME    # Enable at boot
systemctl disable NAME   # Disable at boot
```

### Processes
```bash
ps aux                   # All processes
top                      # Real-time view
htop                     # Better top
kill PID                 # Kill process
killall NAME             # Kill by name
```

### Network
```bash
ip addr show             # IP addresses
ip route show            # Routing table
ss -tuln                 # Open ports
ping HOST                # Test connectivity
traceroute HOST          # Trace route
```

### Disk
```bash
df -h                    # Disk usage
du -sh DIR               # Directory size
lsblk                    # Block devices
mount                    # Mounted filesystems
```

### Logs
```bash
journalctl -f            # Follow logs
journalctl -b            # Boot logs
journalctl -u SERVICE    # Service logs
tail -f /var/log/syslog  # Follow syslog
```

---

This completes the System Administration guide! You now have comprehensive knowledge of:
- systemd and service management
- Networking configuration
- Storage management (partitions, LVM, RAID)
- User and permission management
- Process management
- Security hardening
- Boot process and kernel management
- System monitoring and troubleshooting
- Backup strategies
- Performance tuning

These are the core skills needed to manage Linux systems and build your custom Debian-based OS!