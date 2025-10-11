# Linux File System Hierarchy - Complete Guide

## Introduction

The Linux file system follows a **hierarchical tree structure** starting from the root directory `/`. Unlike Windows (C:\, D:\), everything in Linux is under one unified tree, including external drives, network shares, and devices.

**Key Concept**: "Everything is a file" - In Linux, hardware devices, processes, and system information are represented as files in the filesystem.

---

## The Root Directory (`/`)

The **root directory** is the top-level directory. All other directories branch from here.

```
/
├── bin/
├── boot/
├── dev/
├── etc/
├── home/
├── lib/
├── media/
├── mnt/
├── opt/
├── proc/
├── root/
├── run/
├── sbin/
├── srv/
├── sys/
├── tmp/
├── usr/
└── var/
```

---

## Essential Directories Explained

### `/bin` - Essential User Binaries

**Purpose**: Contains essential command-line programs (binaries) needed for basic system operations and repair.

**What's inside**:
- Basic commands: `ls`, `cp`, `mv`, `rm`, `cat`, `echo`
- Shell: `bash`, `sh`
- System utilities: `ps`, `grep`, `tar`

**Why it matters**: These programs must be available even when other filesystems aren't mounted (like in single-user/recovery mode).

**Example**:
```bash
ls /bin/
# Shows: bash, cat, chmod, cp, date, echo, grep, ls, mkdir, etc.
```

**Note**: On modern systems (Debian 10+), `/bin` is a symlink to `/usr/bin`.

---

### `/boot` - Boot Loader Files

**Purpose**: Contains everything needed to boot the system.

**What's inside**:
- **Kernel files**: `vmlinuz-*` (the Linux kernel)
- **Initial RAM disk**: `initrd.img-*` or `initramfs-*` (temporary filesystem loaded at boot)
- **Boot loader config**: GRUB configuration files
- **System.map**: Kernel symbol table

**Structure**:
```
/boot/
├── grub/              # GRUB bootloader configuration
│   └── grub.cfg       # Main GRUB config
├── vmlinuz-5.10.0-21  # Linux kernel
├── initrd.img-5.10.0-21  # Initial ramdisk
└── System.map-5.10.0-21  # Kernel symbols
```

**Why it matters**: Without these files, your system cannot boot.

**Warning**: Never delete files from `/boot` unless you know exactly what you're doing!

---

### `/dev` - Device Files

**Purpose**: Contains device files that represent hardware and virtual devices.

**What's inside**:
- **Block devices**: Hard drives, USB drives (`sda`, `sdb`, `nvme0n1`)
- **Character devices**: Keyboards, mice, serial ports
- **Pseudo devices**: `/dev/null`, `/dev/zero`, `/dev/random`
- **Terminal devices**: `tty`, `pts/0`

**Common devices**:
```
/dev/sda          # First SATA/SCSI disk
/dev/sda1         # First partition on sda
/dev/nvme0n1      # First NVMe drive
/dev/nvme0n1p1    # First partition on NVMe drive
/dev/null         # Black hole (discards all data)
/dev/zero         # Produces null bytes
/dev/random       # Random number generator
/dev/urandom      # Faster random number generator
/dev/tty          # Current terminal
```

**How it works**: These are NOT regular files. They're special files managed by the kernel. When you read/write to them, you're communicating with hardware or kernel subsystems.

**Example usage**:
```bash
# Discard output (send to black hole)
command > /dev/null

# Create a 100MB file filled with zeros
dd if=/dev/zero of=file.img bs=1M count=100

# Check disk devices
lsblk
```

---

### `/etc` - Configuration Files

**Purpose**: Contains system-wide configuration files. "Editable Text Configuration"

**What's inside**:
- Network configuration: `/etc/network/`, `/etc/hosts`, `/etc/resolv.conf`
- User authentication: `/etc/passwd`, `/etc/shadow`, `/etc/group`
- System services: `/etc/systemd/`
- Application configs: `/etc/apache2/`, `/etc/ssh/`
- Startup scripts: `/etc/init.d/`

**Important files**:

| File | Purpose |
|------|---------|
| `/etc/passwd` | User account information |
| `/etc/shadow` | Encrypted passwords (restricted access) |
| `/etc/group` | Group information |
| `/etc/hosts` | Static hostname to IP mapping |
| `/etc/hostname` | System's hostname |
| `/etc/fstab` | Filesystem mount configuration |
| `/etc/apt/sources.list` | APT repository sources (Debian) |
| `/etc/resolv.conf` | DNS resolver configuration |
| `/etc/sudoers` | Sudo permissions |

**Key concept**: Files in `/etc` are TEXT files - you can edit them with a text editor (as root).

**Example**:
```bash
# View system hostname
cat /etc/hostname

# View user accounts
cat /etc/passwd

# Edit APT sources (as root)
sudo nano /etc/apt/sources.list
```

---

### `/home` - User Home Directories

**Purpose**: Contains personal directories for each user.

**Structure**:
```
/home/
├── john/
│   ├── Documents/
│   ├── Downloads/
│   ├── Desktop/
│   ├── .bashrc        # User's bash configuration
│   └── .config/       # User application configs
├── sarah/
└── mike/
```

**What's stored here**:
- Personal files and documents
- User-specific configurations (hidden files starting with `.`)
- Downloads, pictures, videos
- Application data and settings

**Permissions**: Each user owns their home directory and typically can't access others' directories.

**Hidden files**: Files starting with `.` are hidden configuration files (dotfiles).

**Example**:
```bash
# Go to your home directory
cd ~
# or
cd /home/yourusername

# List all files including hidden ones
ls -la

# View your bash config
cat ~/.bashrc
```

---

### `/lib` and `/lib64` - Shared Libraries

**Purpose**: Contains shared libraries needed by programs in `/bin` and `/sbin`.

**What are libraries?**: Think of them as code that multiple programs share (like DLLs in Windows).

**What's inside**:
- C library: `libc.so.*`
- System libraries: `libsystemd.so`, `libm.so`
- Kernel modules: `/lib/modules/`

**Structure**:
```
/lib/
├── modules/           # Kernel modules (drivers)
│   └── 5.10.0-21/
├── systemd/          # Systemd units and helpers
├── x86_64-linux-gnu/ # Architecture-specific libraries
└── firmware/         # Hardware firmware files
```

**Note**: `/lib64` contains 64-bit libraries, `/lib32` (if present) has 32-bit libraries.

**Example**:
```bash
# List loaded kernel modules
lsmod

# View library dependencies of a program
ldd /bin/ls
```

---

### `/media` - Removable Media Mount Points

**Purpose**: Automatically created mount points for removable media.

**What's inside**:
- USB drives
- CD/DVD drives
- External hard drives
- SD cards

**How it works**: When you plug in a USB drive, the system automatically creates a directory here (like `/media/username/USB_DRIVE`) and mounts the device.

**Example**:
```
/media/
└── john/
    ├── USB_DRIVE/
    └── External_HDD/
```

---

### `/mnt` - Temporary Mount Point

**Purpose**: Manual mount point for temporarily mounting filesystems.

**Usage**: System administrators use this for manually mounting drives, network shares, or ISO files.

**Example**:
```bash
# Mount an ISO file
sudo mount -o loop image.iso /mnt

# Mount a network share
sudo mount -t cifs //server/share /mnt

# Unmount
sudo umount /mnt
```

**Difference from `/media`**: `/media` is for automatic mounting, `/mnt` is for manual/temporary mounts.

---

### `/opt` - Optional Software

**Purpose**: Third-party and optional software packages.

**What's inside**:
- Proprietary software: Google Chrome, Sublime Text
- Large commercial applications
- Manually installed software that doesn't fit the standard structure

**Structure**:
```
/opt/
├── google/
│   └── chrome/
├── sublime_text/
└── lampp/            # XAMPP installation
```

**Why separate?**: Keeps third-party software isolated from system packages, making it easier to manage and remove.

---

### `/proc` - Process Information (Virtual Filesystem)

**Purpose**: Virtual filesystem providing information about running processes and kernel.

**Key concept**: These are NOT real files on disk! They're generated by the kernel on-the-fly.

**What's inside**:
- Process information: `/proc/[PID]/` (each running process has a directory)
- System information: CPU, memory, kernel settings
- Hardware information

**Important files/directories**:

| Location | Information |
|----------|-------------|
| `/proc/cpuinfo` | CPU details |
| `/proc/meminfo` | Memory usage |
| `/proc/version` | Kernel version |
| `/proc/cmdline` | Kernel boot parameters |
| `/proc/[PID]/` | Process-specific information |
| `/proc/sys/` | Kernel parameters (tunable) |

**Example**:
```bash
# View CPU information
cat /proc/cpuinfo

# View memory information
cat /proc/meminfo

# View process command line
cat /proc/1234/cmdline  # Replace 1234 with actual PID

# Modify kernel parameter
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
```

---

### `/root` - Root User Home Directory

**Purpose**: Home directory for the root (superuser) account.

**Important**: This is NOT the root directory (`/`). It's the home directory for the root user.

**Location**: `/root` (not `/home/root`)

**Why separate?**: Kept separate from `/home` because:
- Available even if `/home` is on a separate partition that fails to mount
- Enhanced security separation

**Access**: Only the root user can access this directory.

---

### `/run` - Runtime Data

**Purpose**: Stores runtime data since last boot (temporary).

**What's inside**:
- Process IDs (PID files)
- Socket files
- Lock files
- System state information

**Key concept**: Contents are cleared on reboot. Stored in RAM (tmpfs).

**Example**:
```
/run/
├── systemd/          # Systemd runtime data
├── lock/             # Lock files
├── user/             # User-specific runtime data
└── utmp              # Currently logged-in users
```

---

### `/sbin` - System Binaries

**Purpose**: Essential system administration programs.

**What's inside**:
- System management: `fdisk`, `fsck`, `mkfs`
- Network configuration: `ifconfig`, `route`, `iptables`
- Service management: `shutdown`, `reboot`, `init`

**Who uses it?**: Primarily root/administrators (though regular users can run some commands).

**Example commands**:
```bash
# Check disk usage
df -h

# Partition management
sudo fdisk -l

# Reboot system
sudo reboot

# Check filesystem
sudo fsck /dev/sda1
```

**Note**: On modern systems, `/sbin` is often a symlink to `/usr/sbin`.

---

### `/srv` - Service Data

**Purpose**: Data for services provided by the system.

**What's inside**:
- Web server files: `/srv/www/` or `/srv/http/`
- FTP server files: `/srv/ftp/`
- Version control repositories: `/srv/git/`

**Usage**: Keeps service data organized and separate from application files.

**Example**:
```
/srv/
├── www/              # Web server root
│   └── mywebsite/
├── ftp/              # FTP server data
└── git/              # Git repositories
```

---

### `/sys` - System Information (Virtual Filesystem)

**Purpose**: Virtual filesystem exposing kernel and hardware information.

**Key concept**: Like `/proc`, these are NOT real files. They're interfaces to kernel data.

**What's inside**:
- Device information: `/sys/class/`, `/sys/devices/`
- Power management: `/sys/power/`
- Block devices: `/sys/block/`
- Network devices: `/sys/class/net/`

**Use cases**: Device management, hardware configuration, kernel module parameters.

**Example**:
```bash
# List network interfaces
ls /sys/class/net/

# View disk information
cat /sys/block/sda/size

# View battery status (laptops)
cat /sys/class/power_supply/BAT0/capacity
```

---

### `/tmp` - Temporary Files

**Purpose**: Temporary storage for applications and users.

**Characteristics**:
- World-writable (anyone can create files)
- Files may be deleted on reboot
- Often mounted as tmpfs (RAM-based)
- Cleaned periodically by system

**What's inside**:
- Temporary application data
- Session files
- Cache files

**Security note**: Use with caution - anyone can read/write files here (unless you set proper permissions).

**Example**:
```bash
# Create temporary file
mktemp /tmp/myfile.XXXXXX

# Create temporary directory
mktemp -d /tmp/mydir.XXXXXX
```

---

### `/usr` - User System Resources

**Purpose**: Contains the majority of user utilities and applications (despite the name, NOT user files).

**Historical note**: Originally stood for "Unix System Resources" or contained user directories, but evolved into system-wide programs and data.

**Structure**:
```
/usr/
├── bin/              # User commands (most programs)
├── sbin/             # System administration programs
├── lib/              # Libraries for /usr/bin and /usr/sbin
├── local/            # Locally installed software
├── share/            # Architecture-independent data
├── src/              # Source code (kernel sources)
├── include/          # C header files
└── games/            # Games and educational programs
```

**Sub-directories explained**:

#### `/usr/bin` - User Binaries
- Non-essential commands (most programs you use daily)
- Examples: `python`, `gcc`, `vim`, `firefox`, `git`

#### `/usr/sbin` - System Administration Binaries
- Non-essential system administration programs
- Examples: `useradd`, `groupadd`, `cron`

#### `/usr/lib` - User Libraries
- Libraries for programs in `/usr/bin` and `/usr/sbin`

#### `/usr/local` - Local Software
- For software compiled/installed locally (not from package manager)
- Mirrors structure: `/usr/local/bin`, `/usr/local/lib`, etc.
- Keeps locally installed software separate from package-managed software

#### `/usr/share` - Shared Data
- Architecture-independent files
- Documentation: `/usr/share/doc/`
- Man pages: `/usr/share/man/`
- Icons and themes: `/usr/share/icons/`, `/usr/share/themes/`
- Application data: `/usr/share/applications/`

**Example**:
```bash
# Most installed programs are here
ls /usr/bin/ | wc -l  # Typically 1000+ programs

# View program documentation
ls /usr/share/doc/

# Read man pages source
ls /usr/share/man/man1/
```

---

### `/var` - Variable Data

**Purpose**: Variable data that changes during system operation.

**What's inside**:
- Log files: `/var/log/`
- Package cache: `/var/cache/`
- Spool files: `/var/spool/`
- Temporary files: `/var/tmp/`
- Website data: `/var/www/`
- Databases: `/var/lib/`

**Structure**:
```
/var/
├── log/              # Log files
│   ├── syslog        # System logs
│   ├── auth.log      # Authentication logs
│   └── apache2/      # Web server logs
├── cache/            # Application cache
│   └── apt/          # APT package cache
├── lib/              # Variable state data
│   ├── dpkg/         # Package database
│   └── mysql/        # MySQL databases
├── spool/            # Spool files (print, mail, cron)
├── tmp/              # Temporary files (preserved across reboots)
├── www/              # Web server content
└── mail/             # User mailboxes
```

**Important sub-directories**:

#### `/var/log` - System Logs
Critical for troubleshooting!

| Log File | Purpose |
|----------|---------|
| `/var/log/syslog` | General system logs |
| `/var/log/auth.log` | Authentication attempts |
| `/var/log/kern.log` | Kernel messages |
| `/var/log/dmesg` | Boot messages |
| `/var/log/apt/` | Package management logs |

**Example**:
```bash
# View recent system logs
sudo tail -f /var/log/syslog

# Check failed login attempts
sudo grep "Failed password" /var/log/auth.log

# View boot messages
dmesg | less
```

#### `/var/cache` - Application Cache
- APT package cache: `/var/cache/apt/archives/`
- Can be safely cleaned to free space

#### `/var/lib` - State Information
- Package database: `/var/lib/dpkg/`
- Database files (MySQL, PostgreSQL)
- Application state

---

## Special Concepts

### Mount Points

**What is mounting?**: Attaching a filesystem to a directory in the tree.

**Example**: When you insert a USB drive, the system mounts it to `/media/username/USB_DRIVE/`. The USB's filesystem becomes accessible through that directory.

**View mounted filesystems**:
```bash
# Show all mounted filesystems
mount

# Show disk usage of mounted filesystems
df -h

# View mount configuration
cat /etc/fstab
```

### Symbolic Links (Symlinks)

**What are they?**: Shortcuts/pointers to other files or directories.

**Modern Linux trend**: Many directories are now symlinks:
- `/bin` → `/usr/bin`
- `/sbin` → `/usr/sbin`
- `/lib` → `/usr/lib`

**View symlinks**:
```bash
ls -la /bin
# Output: lrwxrwxrwx ... /bin -> usr/bin
```

---

## File Types in Linux

When you run `ls -l`, the first character indicates file type:

| Symbol | Type | Description |
|--------|------|-------------|
| `-` | Regular file | Normal file |
| `d` | Directory | Folder |
| `l` | Symbolic link | Shortcut |
| `b` | Block device | Hard drive, USB |
| `c` | Character device | Keyboard, terminal |
| `s` | Socket | Inter-process communication |
| `p` | Named pipe | Inter-process communication |

**Example**:
```bash
ls -la /dev/
# Shows different file types (b, c, l)
```

---

## Filesystem Hierarchy Standard (FHS)

The Linux filesystem follows the **Filesystem Hierarchy Standard (FHS)**, which defines the directory structure and directory contents.

**Goals**:
- Consistency across distributions
- Predictable file locations
- Easier software development
- Better system administration

**Debian compliance**: Debian strictly follows FHS, making your custom OS compatible with standard Linux tools and documentation.

---

## Practical Navigation Commands

```bash
# Print working directory (where am I?)
pwd

# Change directory
cd /etc
cd ~              # Go home
cd ..             # Go up one level
cd -              # Go to previous directory

# List files
ls                # Basic list
ls -l             # Long format (detailed)
ls -la            # Include hidden files
ls -lh            # Human-readable sizes

# Tree view (install with: sudo apt install tree)
tree /etc
tree -L 2 /usr    # Limit depth to 2 levels

# Find files
find /etc -name "*.conf"
locate filename   # Fast search (uses database)

# Disk usage
du -sh /var/*     # Size of each directory in /var
df -h             # Disk space usage of mounted filesystems
```

---

## Best Practices for Your Custom OS

1. **Never modify standard directories**: Follow FHS strictly
2. **Custom software location**: Put your custom packages in `/opt/yourOS-name/` or `/usr/local/`
3. **Configuration**: Your OS configs should be in `/etc/yourOS-name/`
4. **Documentation**: Place in `/usr/share/doc/yourOS-name/`
5. **Logs**: Application logs in `/var/log/yourOS-name/`

---

## Quick Reference Summary

| Directory | Purpose | Can Users Write? | Critical? |
|-----------|---------|------------------|-----------|
| `/` | Root of filesystem | No | Yes |
| `/bin` | Essential commands | No | Yes |
| `/boot` | Boot files | No | Yes |
| `/dev` | Device files | No | Yes |
| `/etc` | Configuration | No | Yes |
| `/home` | User files | Yes (own dir) | No |
| `/lib` | Essential libraries | No | Yes |
| `/media` | Removable media | Auto | No |
| `/mnt` | Temp mounts | No | No |
| `/opt` | Optional software | No | No |
| `/proc` | Process info (virtual) | No | Yes |
| `/root` | Root's home | No | Yes |
| `/run` | Runtime data | No | No |
| `/sbin` | System admin tools | No | Yes |
| `/srv` | Service data | No | No |
| `/sys` | System info (virtual) | No | Yes |
| `/tmp` | Temporary files | Yes | No |
| `/usr` | User programs | No | Yes |
| `/var` | Variable data | No | Yes |

---

## Next Steps for Learning

1. **Explore your system**: Navigate through each directory and examine files
2. **Practice commands**: Use `ls`, `cd`, `cat`, `file` to explore
3. **Read logs**: Check `/var/log/` to understand system events
4. **Check configurations**: View files in `/etc/` to see how things are configured
5. **Experiment safely**: Use a VM or container to practice without breaking your system

**Remember**: Understanding the filesystem hierarchy is fundamental to Linux mastery. This knowledge applies to system administration, package creation, and building your custom OS!