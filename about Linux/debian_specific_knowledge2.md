# Debian-Specific Knowledge - Complete Guide

## Introduction

Debian is one of the oldest and most influential Linux distributions. Understanding Debian-specific systems is crucial for building your own Debian-based OS. This guide covers everything that makes Debian unique.

---

## 1. The Debian Package System (.deb)

### What is a Debian Package?

A **`.deb`** file is Debian's package format - a compressed archive containing:
- Program files (binaries, libraries, data)
- Metadata (package name, version, dependencies)
- Installation/removal scripts
- Configuration files

**Think of it as**: An installer that knows how to install, configure, and remove software properly.

### Anatomy of a .deb Package

A `.deb` file is actually an **ar archive** containing three parts:

```
package.deb
├── debian-binary          # Version of deb format (usually "2.0")
├── control.tar.xz         # Package metadata and scripts
│   ├── control            # Package information
│   ├── preinst            # Pre-installation script
│   ├── postinst           # Post-installation script
│   ├── prerm              # Pre-removal script
│   ├── postrm             # Post-removal script
│   ├── conffiles          # List of configuration files
│   └── md5sums            # File checksums
└── data.tar.xz            # Actual files to install
    ├── usr/
    │   └── bin/
    │       └── program
    ├── etc/
    │   └── program.conf
    └── usr/share/doc/
```

### The Control File

The **control** file contains essential metadata:

```
Package: myprogram
Version: 1.0.5-1
Section: utils
Priority: optional
Architecture: amd64
Depends: libc6 (>= 2.31), libssl1.1
Recommends: ca-certificates
Suggests: documentation
Conflicts: oldprogram
Replaces: oldprogram (<< 1.0)
Maintainer: Your Name <you@example.com>
Description: Short one-line description
 Extended description with more details.
 Can span multiple lines, each starting with a space.
Homepage: https://example.com
```

**Key fields explained**:

| Field | Purpose | Example |
|-------|---------|---------|
| `Package` | Package name (lowercase, no spaces) | `firefox` |
| `Version` | Version number | `1.0.5-1` |
| `Section` | Category | `utils`, `net`, `devel` |
| `Priority` | Importance level | `required`, `important`, `standard`, `optional` |
| `Architecture` | CPU architecture | `amd64`, `arm64`, `all` |
| `Depends` | Required packages | `libc6 (>= 2.31)` |
| `Maintainer` | Package maintainer | `name <email>` |
| `Description` | What the package does | Short + extended description |

### Version Numbers in Debian

Debian uses a specific version format: **`EPOCH:UPSTREAM-REVISION`**

**Examples**:
```
1.0.5-1          # Upstream version 1.0.5, Debian revision 1
2:1.2.3-4        # Epoch 2, upstream 1.2.3, revision 4
1.0~rc1-1        # Release candidate (~ sorts before normal releases)
1.0+dfsg-1       # Modified upstream (DFSG compliant)
```

**Components**:
- **Epoch**: Used when version numbering changes (rare). Default is 0.
- **Upstream**: Version from original developers
- **Revision**: Debian-specific changes (packaging changes)

**Special characters**:
- `~` (tilde): Sorts BEFORE normal releases (for alpha/beta/rc)
- `+` (plus): Additional information (doesn't affect sorting)

### Maintainer Scripts

These scripts run at different stages of package lifecycle:

#### **preinst** (Pre-installation)
Runs BEFORE package files are unpacked.
```bash
#!/bin/bash
set -e

# Example: Stop service before upgrade
if [ "$1" = "upgrade" ]; then
    systemctl stop myservice
fi
```

#### **postinst** (Post-installation)
Runs AFTER package files are installed.
```bash
#!/bin/bash
set -e

# Example: Start service after installation
if [ "$1" = "configure" ]; then
    systemctl enable myservice
    systemctl start myservice
fi
```

#### **prerm** (Pre-removal)
Runs BEFORE package removal.
```bash
#!/bin/bash
set -e

# Example: Stop service before removal
if [ "$1" = "remove" ]; then
    systemctl stop myservice
fi
```

#### **postrm** (Post-removal)
Runs AFTER package removal.
```bash
#!/bin/bash
set -e

# Example: Clean up after removal
if [ "$1" = "purge" ]; then
    rm -rf /var/lib/myprogram
fi
```

**Script arguments**: Scripts receive arguments like `install`, `upgrade`, `remove`, `purge` to know what action is being performed.

### Dependencies

Debian has sophisticated dependency management:

#### **Depends**
Must be installed for the package to work.
```
Depends: python3 (>= 3.9), libssl1.1
```

#### **Recommends**
Should be installed (strongly suggested), but not required.
```
Recommends: ca-certificates, python3-pip
```

#### **Suggests**
Optional packages that enhance functionality.
```
Suggests: python3-dev, documentation
```

#### **Pre-Depends**
Must be installed AND configured BEFORE this package.
```
Pre-Depends: dpkg (>= 1.17)
```

#### **Conflicts**
Cannot be installed alongside this package.
```
Conflicts: apache2
```

#### **Breaks**
This package breaks the specified packages.
```
Breaks: oldversion (<< 2.0)
```

#### **Replaces**
Files from this package can replace files from another.
```
Replaces: oldpackage
```

#### **Provides**
This package provides the functionality of another (virtual package).
```
Provides: mail-transport-agent
```

### Working with .deb Files

```bash
# View package information
dpkg-deb -I package.deb

# View package contents (file list)
dpkg-deb -c package.deb

# Extract package contents
dpkg-deb -x package.deb /tmp/extracted

# Extract control information
dpkg-deb -e package.deb /tmp/control

# Install a .deb file
sudo dpkg -i package.deb

# Remove installed package
sudo dpkg -r packagename

# Purge (remove including config files)
sudo dpkg -P packagename

# Fix broken dependencies after dpkg -i
sudo apt-get install -f
```

### Building a Simple .deb Package

**Directory structure**:
```
mypackage-1.0/
├── DEBIAN/
│   ├── control         # Required
│   ├── postinst        # Optional
│   └── prerm           # Optional
├── usr/
│   ├── bin/
│   │   └── myprogram
│   └── share/
│       └── doc/
│           └── mypackage/
│               └── README
└── etc/
    └── myprogram.conf
```

**Build command**:
```bash
# Build the package
dpkg-deb --build mypackage-1.0

# This creates: mypackage-1.0.deb
```

**Example control file**:
```
Package: mypackage
Version: 1.0-1
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Your Name <you@example.com>
Description: My custom program
 This is a longer description of what
 my program does.
```

---

## 2. APT (Advanced Package Tool)

### What is APT?

**APT** is Debian's high-level package management system. It:
- Resolves dependencies automatically
- Downloads packages from repositories
- Handles package installation, upgrade, and removal
- Manages package configurations

**Architecture**:
```
APT (User Interface)
    ↓
apt/apt-get/apt-cache (Commands)
    ↓
libapt (Library)
    ↓
dpkg (Low-level installer)
```

### APT vs apt-get vs dpkg

| Tool | Level | Use Case |
|------|-------|----------|
| `dpkg` | Low-level | Install/remove individual .deb files |
| `apt-get` | High-level | Full package management with dependencies |
| `apt-cache` | Query tool | Search and show package information |
| `apt` | Modern unified | Combines apt-get and apt-cache (user-friendly) |

### Repository Configuration

#### **/etc/apt/sources.list**

The main configuration file for package sources:

```bash
# Format: deb [options] uri distribution [component1 component2 ...]

# Main Debian repositories
deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware

# Security updates
deb http://security.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware

# Updates
deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware

# Backports (newer software)
deb http://deb.debian.org/debian bookworm-backports main contrib non-free non-free-firmware
```

**Components explained**:

| Component | Description |
|-----------|-------------|
| `main` | Free and open-source software (DFSG-compliant) |
| `contrib` | Free software that depends on non-free software |
| `non-free` | Non-free software (proprietary) |
| `non-free-firmware` | Non-free firmware (hardware drivers) |

**Distribution names**:
- `bookworm` - Debian 12 (current stable)
- `bullseye` - Debian 11 (oldstable)
- `sid` - Unstable (rolling release)
- `testing` - Testing (future release)

#### **/etc/apt/sources.list.d/**

Additional repository files (one file per repository):

```bash
# Example: /etc/apt/sources.list.d/docker.list
deb [arch=amd64 signed-by=/usr/share/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable
```

### APT Commands Reference

#### **Updating Package Lists**
```bash
# Update package list from repositories
sudo apt update

# OR (older command)
sudo apt-get update
```

#### **Upgrading Packages**
```bash
# Upgrade all packages (safe)
sudo apt upgrade

# Upgrade + install/remove packages as needed
sudo apt full-upgrade

# Upgrade from one release to another
sudo apt dist-upgrade
```

#### **Installing Packages**
```bash
# Install a package
sudo apt install packagename

# Install multiple packages
sudo apt install package1 package2 package3

# Install from a specific repository (backports)
sudo apt install -t bookworm-backports packagename

# Install a .deb file and resolve dependencies
sudo apt install ./package.deb

# Reinstall a package
sudo apt install --reinstall packagename

# Install without installing recommended packages
sudo apt install --no-install-recommends packagename
```

#### **Removing Packages**
```bash
# Remove package (keep configuration files)
sudo apt remove packagename

# Remove package and configuration files
sudo apt purge packagename

# Remove automatically installed dependencies no longer needed
sudo apt autoremove

# Remove package, config, and dependencies
sudo apt purge packagename && sudo apt autoremove
```

#### **Searching Packages**
```bash
# Search for a package
apt search keyword

# Show package details
apt show packagename

# List all available versions
apt list packagename -a

# Show installed packages
apt list --installed

# Show upgradable packages
apt list --upgradable
```

#### **Package Information**
```bash
# Show package details
apt show packagename

# Show dependencies
apt depends packagename

# Show reverse dependencies (what depends on this)
apt rdepends packagename

# Show package changelog
apt changelog packagename
```

#### **Package Files**
```bash
# List files installed by a package
dpkg -L packagename

# Find which package owns a file
dpkg -S /path/to/file

# Search for a file in packages (need apt-file)
apt-file search filename
```

#### **Holding Packages**
```bash
# Prevent package from being upgraded
sudo apt-mark hold packagename

# Allow package to be upgraded again
sudo apt-mark unhold packagename

# Show held packages
apt-mark showhold
```

#### **Cleaning Cache**
```bash
# Clean downloaded package files
sudo apt clean

# Remove old package files
sudo apt autoclean

# Show cache size
du -sh /var/cache/apt/archives/
```

### APT Configuration

#### **/etc/apt/apt.conf** and **/etc/apt/apt.conf.d/**

Configuration files for APT behavior:

```bash
# Example: /etc/apt/apt.conf.d/99custom
APT::Install-Recommends "false";
APT::Install-Suggests "false";
APT::Get::Assume-Yes "false";

# Proxy configuration
Acquire::http::Proxy "http://proxy.example.com:8080";

# Timeout settings
Acquire::http::Timeout "60";
```

### Package Pinning and Priorities

Control which version of packages to install when multiple versions are available.

#### **/etc/apt/preferences** or **/etc/apt/preferences.d/**

```bash
# Prefer packages from stable
Package: *
Pin: release a=stable
Pin-Priority: 900

# Allow packages from backports, but don't install automatically
Package: *
Pin: release a=bookworm-backports
Pin-Priority: 100

# Pin a specific package to a specific version
Package: nginx
Pin: version 1.18.*
Pin-Priority: 1001
```

**Priority values**:
- `1000+` - Install even if it means downgrading
- `990-999` - Install if not already installed
- `500-989` - Install if higher version than current
- `100-499` - Install only if explicitly requested
- `0-99` - Never install
- `<0` - Never install, even explicitly

### Working with Package Cache

```bash
# View package cache policy
apt-cache policy packagename

# Example output:
# packagename:
#   Installed: 1.0-1
#   Candidate: 1.2-1
#   Version table:
#      1.2-1 500
#         500 http://deb.debian.org/debian bookworm/main amd64 Packages
#  *** 1.0-1 100
#         100 /var/lib/dpkg/status

# Search package descriptions
apt-cache search keyword

# Show package stats
apt-cache stats

# Show unmet dependencies
apt-cache unmet
```

---

## 3. Debian Policy Manual

### What is Debian Policy?

The **Debian Policy Manual** is a set of standards that all Debian packages must follow. It ensures:
- Consistency across packages
- System stability
- Interoperability
- Quality standards

**Why it matters for your OS**: Following Debian Policy ensures your packages work correctly with existing Debian tools and infrastructure.

### Key Policy Requirements

#### **File System Hierarchy**
- Packages must install files in standard locations
- Must not modify files in `/usr/local`
- Configuration files go in `/etc`
- Documentation in `/usr/share/doc/packagename`

#### **Package Naming**
- Lowercase letters, digits, `-` and `+` only
- Must start with lowercase letter or digit
- No uppercase, no underscores

**Examples**:
```
✓ my-program
✓ python3-requests
✓ lib64gcc-s1
✗ My-Program (uppercase)
✗ my_program (underscore)
```

#### **Version Numbering**
Follow format: `[epoch:]upstream_version[-debian_revision]`
```
1.0-1           # Upstream 1.0, Debian revision 1
2:1.2.3-4       # Epoch 2
1.0~beta1-1     # Beta version (sorts before 1.0)
```

#### **Dependencies**
- Must declare all dependencies
- Use version constraints when needed:
  - `>=` - Greater than or equal
  - `<=` - Less than or equal
  - `<<` - Strictly less than
  - `>>` - Strictly greater than
  - `=` - Exactly equal

```
Depends: libc6 (>= 2.31), python3 (>= 3.9)
```

#### **Configuration Files**
- Configuration files must be in `/etc`
- Must be marked as `conffiles`
- APT asks before overwriting modified config files

#### **Documentation**
Every package must include:
- Copyright file: `/usr/share/doc/packagename/copyright`
- Changelog: `/usr/share/doc/packagename/changelog.Debian.gz`
- May include: README, NEWS, TODO

#### **Package Sections**
Packages must be in one section:

| Section | Purpose |
|---------|---------|
| `admin` | System administration utilities |
| `cli-mono` | Mono/CLI infrastructure |
| `comm` | Communication programs |
| `database` | Database servers and clients |
| `debug` | Debug symbols |
| `devel` | Development tools |
| `doc` | Documentation |
| `editors` | Text editors |
| `education` | Educational software |
| `electronics` | Electronics-related programs |
| `embedded` | Embedded systems |
| `fonts` | Font packages |
| `games` | Games |
| `gnome` | GNOME desktop |
| `gnu-r` | GNU R statistical system |
| `gnustep` | GNUstep environment |
| `graphics` | Graphics software |
| `hamradio` | Amateur radio |
| `haskell` | Haskell environment |
| `httpd` | Web servers |
| `interpreters` | Interpreters |
| `introspection` | GObject introspection |
| `java` | Java environment |
| `javascript` | JavaScript |
| `kde` | KDE desktop |
| `kernel` | Kernel and modules |
| `libdevel` | Development libraries |
| `libs` | Runtime libraries |
| `lisp` | Lisp environment |
| `localization` | Localization and translations |
| `mail` | Email clients and servers |
| `math` | Mathematics software |
| `metapackages` | Meta-packages |
| `misc` | Miscellaneous |
| `net` | Network tools |
| `news` | Usenet |
| `ocaml` | OCaml environment |
| `oldlibs` | Obsolete libraries |
| `otherosfs` | Other OS filesystems |
| `perl` | Perl environment |
| `php` | PHP |
| `python` | Python environment |
| `ruby` | Ruby environment |
| `rust` | Rust environment |
| `science` | Scientific software |
| `shells` | Shells |
| `sound` | Audio software |
| `tasks` | Task packages |
| `tex` | TeX system |
| `text` | Text processing |
| `utils` | Utilities |
| `vcs` | Version control systems |
| `video` | Video software |
| `web` | Web development |
| `x11` | X Window System |
| `xfce` | Xfce desktop |
| `zope` | Zope environment |

#### **Package Priorities**

| Priority | Purpose | Installation |
|----------|---------|--------------|
| `required` | Essential for system | Always installed |
| `important` | Important utilities | Typically installed |
| `standard` | Standard system | Default installation |
| `optional` | Optional packages | Not installed by default |
| `extra` | Specialized/conflicting | User choice |

### Must, Should, May in Policy

Policy uses RFC 2119 keywords:

- **MUST** / **REQUIRED** - Absolute requirement
- **SHOULD** / **RECOMMENDED** - May ignore in rare circumstances
- **MAY** / **OPTIONAL** - Truly optional

### Policy Checkers

Tools to verify policy compliance:

```bash
# Install lintian (policy checker)
sudo apt install lintian

# Check a .deb package
lintian package.deb

# Check source package
lintian -I package.dsc

# Pedantic check (all warnings)
lintian -I --pedantic package.deb
```

**Common lintian tags**:
- **E (Error)**: Policy violation - must fix
- **W (Warning)**: Policy violation - should fix
- **I (Info)**: Informational
- **P (Pedantic)**: Not policy but good practice

---

## 4. Debian Alternatives System

### What is update-alternatives?

A system to manage multiple versions of the same program, allowing users/admins to choose which one to use.

**Common use cases**:
- Multiple Java versions
- Different text editors
- Various web browsers
- Compiler versions

### How It Works

The system creates symbolic links in `/usr/bin` pointing to `/etc/alternatives`, which in turn points to the actual program.

```
/usr/bin/editor → /etc/alternatives/editor → /usr/bin/nano
```

### Managing Alternatives

```bash
# View alternatives for a command
update-alternatives --display editor

# List all alternatives
update-alternatives --list editor

# Set alternative interactively
sudo update-alternatives --config editor

# Set alternative directly
sudo update-alternatives --set editor /usr/bin/vim.basic

# Install a new alternative
sudo update-alternatives --install /usr/bin/editor editor /usr/bin/emacs 50

# Remove an alternative
sudo update-alternatives --remove editor /usr/bin/emacs

# Automatically select best alternative (highest priority)
sudo update-alternatives --auto editor
```

### Alternative Groups

Some alternatives work as groups (like `java`):

```bash
# Java alternatives include:
# - java (binary)
# - javac (compiler)
# - javadoc (documentation)
# All switched together
```

### Creating Alternatives for Your Packages

In your package's `postinst` script:

```bash
#!/bin/bash
set -e

if [ "$1" = "configure" ]; then
    update-alternatives --install \
        /usr/bin/myeditor \        # Link name
        myeditor \                  # Alternative name
        /usr/bin/myeditor-v1 \     # Target path
        50                          # Priority
fi
```

In `prerm` script:

```bash
#!/bin/bash
set -e

if [ "$1" = "remove" ]; then
    update-alternatives --remove myeditor /usr/bin/myeditor-v1
fi
```

---

## 5. Debconf (Configuration Management)

### What is Debconf?

**Debconf** is Debian's configuration management system for package installation. It:
- Asks questions during installation
- Stores answers in a database
- Allows pre-configuration (preseeding)
- Provides consistent interface

### Debconf Priorities

| Priority | Description | When shown |
|----------|-------------|------------|
| `critical` | Essential questions | Always |
| `high` | Important questions | Default setting |
| `medium` | Normal questions | If configured |
| `low` | Minor questions | If configured |

**Set priority**:
```bash
# Configure debconf priority
sudo dpkg-reconfigure debconf

# Or set via environment
export DEBIAN_PRIORITY=critical
```

### Debconf Frontends

Different ways to interact with debconf:

| Frontend | Description |
|----------|-------------|
| `dialog` | Text-based UI (default) |
| `readline` | Command-line prompts |
| `noninteractive` | No questions (use defaults) |
| `gnome` | GTK+ graphical interface |
| `kde` | KDE graphical interface |

**Set frontend**:
```bash
# Temporarily
DEBIAN_FRONTEND=noninteractive sudo apt install package

# System-wide
sudo dpkg-reconfigure debconf
```

### Working with Debconf

```bash
# Show debconf database for a package
debconf-show packagename

# Get a specific value
debconf-get-selections | grep packagename

# Set a value (preseeding)
echo "packagename packagename/question string value" | sudo debconf-set-selections

# Reconfigure package (re-ask questions)
sudo dpkg-reconfigure packagename

# Clear package configuration
echo PURGE | sudo debconf-communicate packagename
```

### Creating Debconf Templates

**File**: `debian/packagename.templates`

```
Template: mypackage/enable-service
Type: boolean
Default: true
Description: Enable mypackage service at boot?
 Should the mypackage service be enabled automatically
 when the system boots?

Template: mypackage/admin-email
Type: string
Default: root@localhost
Description: Administrator email address:
 Please enter the email address of the system administrator.

Template: mypackage/mode
Type: select
Choices: production, development, testing
Default: production
Description: Operating mode:
 Select the operating mode for mypackage.
```

**Question Types**:
- `boolean` - Yes/No question
- `string` - Free text input
- `password` - Hidden text input
- `select` - Choose one from list
- `multiselect` - Choose multiple from list
- `note` - Display information
- `text` - Multi-line text
- `error` - Error message

### Using Debconf in Scripts

In `postinst`:

```bash
#!/bin/bash
set -e

. /usr/share/debconf/confmodule

# Ask question
db_input high mypackage/enable-service || true
db_go || true

# Get answer
db_get mypackage/enable-service
ENABLE_SERVICE="$RET"

if [ "$ENABLE_SERVICE" = "true" ]; then
    systemctl enable mypackage
fi

# Clean up
db_stop
```

### Preseeding

**Preseed file** allows automated installation without questions:

```bash
# mypackage.preseed
mypackage mypackage/enable-service boolean true
mypackage mypackage/admin-email string admin@example.com
mypackage mypackage/mode select production
```

**Use preseed**:
```bash
# Load preseed before installation
sudo debconf-set-selections < mypackage.preseed
sudo apt install mypackage
```

---

## 6. Package Repositories and Management

### Creating Your Own Repository

For your custom OS, you'll need a package repository.

#### **Simple Repository with dpkg-scanpackages**

```bash
# 1. Create repository structure
mkdir -p /var/www/repo/debian/pool/main
mkdir -p /var/www/repo/debian/dists/bookworm/main/binary-amd64

# 2. Copy .deb files
cp *.deb /var/www/repo/debian/pool/main/

# 3. Generate Packages file
cd /var/www/repo/debian
dpkg-scanpackages pool/main /dev/null | gzip -9c > dists/bookworm/main/binary-amd64/Packages.gz

# 4. Create Release file
cat > dists/bookworm/Release <<EOF
Origin: YourOS
Label: YourOS
Suite: stable
Codename: bookworm
Architectures: amd64
Components: main
Description: YourOS Official Repository
EOF
```

#### **Using reprepro (Better Method)**

```bash
# Install reprepro
sudo apt install reprepro

# Create repository directory
mkdir -p /var/www/repo
cd /var/www/repo

# Create configuration
mkdir conf
cat > conf/distributions <<EOF
Origin: YourOS
Label: YourOS
Codename: bookworm
Architectures: amd64 arm64 source
Components: main contrib non-free
Description: YourOS Repository
SignWith: YOUR_GPG_KEY_ID
EOF

# Add package
reprepro includedeb bookworm /path/to/package.deb

# Add source package
reprepro includedsc bookworm /path/to/package.dsc

# List packages
reprepro list bookworm

# Remove package
reprepro remove bookworm packagename

# Update repository
reprepro export bookworm
```

### Signing Repositories

Users need to trust your repository via GPG signing:

```bash
# 1. Generate GPG key
gpg --full-generate-key

# 2. Export public key
gpg --armor --export YOUR_EMAIL > repo-key.gpg

# 3. Users import your key
wget -qO - https://yourrepo.com/repo-key.gpg | sudo apt-key add -
# Or (newer method)
wget -qO - https://yourrepo.com/repo-key.gpg | sudo tee /usr/share/keyrings/youros.gpg

# 4. Add signed repository
echo "deb [signed-by=/usr/share/keyrings/youros.gpg] https://yourrepo.com/debian bookworm main" | sudo tee /etc/apt/sources.list.d/youros.list
```

### Repository Types

#### **Binary Repository**
Contains compiled `.deb` packages.

#### **Source Repository**
Contains source packages (`.dsc`, `.orig.tar.gz`, `.debian.tar.xz`).

```
deb http://repo.example.com/debian bookworm main      # Binary
deb-src http://repo.example.com/debian bookworm main  # Source
```

---

## 7. Debian Build Tools

### dpkg-buildpackage

Main tool for building Debian packages from source:

```bash
# Build binary and source packages
dpkg-buildpackage -b  # Binary only
dpkg-buildpackage -S  # Source only
dpkg-buildpackage     # Both

# Build without signing
dpkg-buildpackage -us -uc

# Build with specific build options
dpkg-buildpackage -j4  # Use 4 CPU cores
```

### debhelper

Set of scripts to simplify package building:

**debian/rules** example:
```makefile
#!/usr/bin/make -f

%:
	dh $@
```

Common debhelper commands:
- `dh_auto_configure` - Run configure script
- `dh_auto_build` - Compile software
- `dh_auto_install` - Install to temp directory
- `dh_installdocs` - Install documentation
- `dh_installman` - Install man pages
- `dh_installsystemd` - Install systemd units
- `dh_compress` - Compress documentation
- `dh_fixperms` - Fix file permissions
- `dh_gencontrol` - Generate control file
- `dh_builddeb` - Build .deb

### pbuilder

Clean build environment (chroot):

```bash
# Install pbuilder
sudo apt install pbuilder

# Create base system
sudo pbuilder create --distribution bookworm

# Build package in clean environment
sudo pbuilder build package.dsc

# Update base system
sudo pbuilder update

# Result in
/var/cache/pbuilder/result/
```

### sbuild

Alternative to pbuilder (used by Debian developers):

```bash
# Install sbuild
sudo apt install sbuild

# Setup
sudo sbuild-update --keygen
sudo sbuild-createchroot --include=eatmydata,ccache bookworm /srv/chroot/bookworm http://deb.debian.org/debian

# Build
sbuild package.dsc
```

---

## 8. Best Practices for Your Custom OS

### Package Naming Convention

For your OS-specific packages:
```
youros-desktop        # Your desktop environment
youros-themes         # Themes
youros-wallpapers     # Wallpapers
youros-settings       # Default settings
youros-installer      # Custom installer
```

### Metapackages

Create metapackages that depend on groups of packages:

```
Package: youros-standard
Depends: youros-desktop, youros-themes, firefox-esr, libreoffice
Description: YourOS standard installation
```

### Version Numbering

For your OS releases:
```
youros-desktop_1.0-1      # First release
youros-desktop_1.0-2      # Bug fix to packaging
youros-desktop_1.1-1      # Feature update
youros-desktop_2.0-1      # Major version
```

### Configuration Management

Create `/etc/youros/` for your OS-specific configs:
```bash
/etc/youros/
├── release           # OS version info
├── repos.conf        # Repository configuration
└── defaults/         # Default settings
    ├── desktop.conf
    └── apps.conf
```

### Branding Files

Important files to customize:

```bash
# OS Release Information
/etc/os-release
/etc/lsb-release
/etc/issue
/etc/issue.net

# GRUB Boot Loader
/etc/default/grub
/boot/grub/themes/

# Desktop Environment
/usr/share/pixmaps/          # Icons
/usr/share/backgrounds/       # Wallpapers
/usr/share/themes/           # GTK/Qt themes
/usr/share/plymouth/themes/  # Boot splash
```

**Example /etc/os-release**:
```bash
NAME="YourOS"
VERSION="1.0 (Codename)"
ID=youros
ID_LIKE=debian
PRETTY_NAME="YourOS 1.0"
VERSION_ID="1.0"
VERSION_CODENAME=codename
HOME_URL="https://youros.org/"
SUPPORT_URL="https://youros.org/support"
BUG_REPORT_URL="https://youros.org/bugs"
LOGO=youros-logo
```

---

## 9. Debian Release Management

### Understanding Debian Releases

Debian has three main branches:

| Branch | Name | Description | Stability |
|--------|------|-------------|-----------|
| `stable` | Current release | Production-ready | Very stable |
| `testing` | Next release | Release candidate | Mostly stable |
| `unstable` | sid | Development | Unstable |
| `experimental` | experimental | Experimental packages | Very unstable |

**Current releases**:
- Debian 12 "Bookworm" (stable)
- Debian 11 "Bullseye" (oldstable)
- Debian 13 "Trixie" (testing)

### Release Cycle

1. **Freeze** - Testing branch freezes, only bug fixes allowed
2. **RC Bug Squashing** - Fix release-critical bugs
3. **Release** - Testing becomes new stable
4. **Support Period** - ~3 years full support, +2 years LTS

### Choosing a Base for Your OS

**Option 1: Stable**
- Pros: Rock solid, predictable, long support
- Cons: Older software
- Best for: Servers, enterprise, conservative users

**Option 2: Testing**
- Pros: Newer software, still tested
- Cons: Occasional breakage, security updates delayed
- Best for: Desktops, power users

**Option 3: Unstable (sid)**
- Pros: Latest software, cutting edge
- Cons: Can break, requires expertise
- Best for: Developers, bleeding edge users

**Recommendation for new OS**: Start with **stable** + **selective backports**

### Backports

Get newer software on stable releases:

```bash
# Enable backports
echo "deb http://deb.debian.org/debian bookworm-backports main contrib non-free" | sudo tee /etc/apt/sources.list.d/backports.list

sudo apt update

# Install from backports
sudo apt install -t bookworm-backports packagename

# Set backports as default for specific package
cat > /etc/apt/preferences.d/backports <<EOF
Package: packagename
Pin: release a=bookworm-backports
Pin-Priority: 990
EOF
```

---

## 10. Advanced Package Management

### Virtual Packages

Virtual packages provide an interface that multiple packages can fulfill:

**Example**: `mail-transport-agent`
- Provided by: postfix, exim4, sendmail
- Any one of these satisfies the dependency

**Common virtual packages**:
- `mail-transport-agent` - Email server
- `x-terminal-emulator` - Terminal emulator
- `x-window-manager` - Window manager
- `www-browser` - Web browser
- `editor` - Text editor

**Creating a virtual package provider**:
```
Package: yourmail
Provides: mail-transport-agent
Conflicts: mail-transport-agent
Replaces: mail-transport-agent
```

### Transitional Packages

Used when package names change:

```
Package: oldpackage
Depends: newpackage
Architecture: all
Priority: optional
Section: oldlibs
Description: transitional package
 This is a transitional package. It can safely be removed.
```

Users upgrade from `oldpackage` → automatically get `newpackage`.

### Multi-Arch Support

Support for multiple architectures (32-bit, 64-bit, ARM):

```
Package: mylib
Architecture: any
Multi-Arch: same
```

**Multi-Arch values**:
- `same` - Can install multiple architectures simultaneously
- `foreign` - Can satisfy dependencies of other architectures
- `allowed` - Can be declared Multi-Arch in dependencies

**Installing multi-arch packages**:
```bash
# Add architecture support
sudo dpkg --add-architecture i386
sudo apt update

# Install 32-bit package on 64-bit system
sudo apt install package:i386
```

---

## 11. Package Building Workflow

### Complete Package Building Process

#### **Step 1: Prepare Source**

```bash
# Create source directory
mkdir mypackage-1.0
cd mypackage-1.0

# Add your program files
mkdir src
echo '#include <stdio.h>
int main() { printf("Hello from mypackage!\n"); return 0; }' > src/main.c

# Create Makefile
cat > Makefile <<'EOF'
PREFIX = /usr
BINDIR = $(PREFIX)/bin

all:
	gcc -o mypackage src/main.c

install:
	install -D -m 0755 mypackage $(DESTDIR)$(BINDIR)/mypackage

clean:
	rm -f mypackage
EOF
```

#### **Step 2: Create debian/ Directory**

```bash
# Initialize debian directory
mkdir debian

# Create required files
cd debian
```

**debian/control**:
```
Source: mypackage
Section: utils
Priority: optional
Maintainer: Your Name <you@example.com>
Build-Depends: debhelper-compat (= 13), gcc
Standards-Version: 4.6.0
Homepage: https://example.com

Package: mypackage
Architecture: any
Depends: ${shlibs:Depends}, ${misc:Depends}
Description: My example package
 This is a longer description of my package.
 It can span multiple lines.
```

**debian/changelog**:
```
mypackage (1.0-1) unstable; urgency=medium

  * Initial release

 -- Your Name <you@example.com>  Fri, 10 Oct 2025 10:00:00 +0000
```

**debian/rules**:
```makefile
#!/usr/bin/make -f

%:
	dh $@
```

**debian/copyright**:
```
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: mypackage
Source: https://example.com

Files: *
Copyright: 2025 Your Name <you@example.com>
License: GPL-3+

License: GPL-3+
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 .
 This package is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 .
 On Debian systems, the complete text of the GNU General
 Public License version 3 can be found in "/usr/share/common-licenses/GPL-3".
```

**debian/compat** (or use debhelper-compat):
```
13
```

#### **Step 3: Build Package**

```bash
# Go to source root
cd ..

# Build package
dpkg-buildpackage -us -uc -b

# Result files in parent directory:
# mypackage_1.0-1_amd64.deb
# mypackage_1.0-1_amd64.build
# mypackage_1.0-1_amd64.buildinfo
# mypackage_1.0-1_amd64.changes
```

#### **Step 4: Test Package**

```bash
# Check with lintian
lintian ../mypackage_1.0-1_amd64.deb

# Test installation
sudo dpkg -i ../mypackage_1.0-1_amd64.deb

# Verify files
dpkg -L mypackage

# Test program
mypackage

# Remove package
sudo apt remove mypackage
```

### Helper Tools

**dh_make** - Create initial debian/ directory:
```bash
# In source directory
dh_make --createorig

# Follow prompts to create basic debian/ structure
```

**debuild** - Build and run lintian:
```bash
# Install
sudo apt install devscripts

# Build
debuild -us -uc
```

---

## 12. Source Package Format

### Source Package Components

A Debian source package consists of 3 files:

1. **`.dsc`** - Debian Source Control (metadata)
2. **`.orig.tar.gz`** - Original upstream source
3. **`.debian.tar.xz`** - Debian-specific changes

**Example**:
```
mypackage_1.0-1.dsc
mypackage_1.0.orig.tar.gz
mypackage_1.0-1.debian.tar.xz
```

### Building from Source

```bash
# Download source package
apt-get source packagename

# Or with specific version
apt-get source packagename=1.0-1

# Extract and build
cd packagename-1.0
dpkg-buildpackage -us -uc -b

# Install build dependencies first
sudo apt-get build-dep packagename
```

### Creating Source Package

```bash
# From working directory
dpkg-buildpackage -S -us -uc

# With original tarball
dpkg-source -b mypackage-1.0
```

---

## 13. Practical Examples for Your OS

### Example 1: Custom Desktop Package

**Package**: `youros-desktop`

```
Package: youros-desktop
Depends: xfce4, 
         youros-themes,
         youros-wallpapers,
         firefox-esr,
         thunderbird,
         libreoffice,
         vlc
Recommends: youros-settings,
            synaptic
Suggests: youros-games
Description: YourOS desktop environment
 This metapackage installs the complete YourOS desktop environment.
```

### Example 2: Theme Package

**Package**: `youros-themes`

**File structure**:
```
youros-themes-1.0/
├── debian/
│   ├── control
│   ├── changelog
│   ├── rules
│   ├── copyright
│   └── install
└── themes/
    ├── YourOS-Dark/
    └── YourOS-Light/
```

**debian/install**:
```
themes/* usr/share/themes/
```

### Example 3: Settings Package

**Package**: `youros-settings`

**debian/postinst**:
```bash
#!/bin/bash
set -e

if [ "$1" = "configure" ]; then
    # Set default wallpaper
    update-alternatives --install /usr/share/backgrounds/desktop-base/default \
        desktop-background \
        /usr/share/backgrounds/youros/default.jpg \
        100
    
    # Configure default applications
    xdg-mime default firefox-esr.desktop x-scheme-handler/http
    xdg-mime default firefox-esr.desktop x-scheme-handler/https
fi
```

---

## 14. Testing and Quality Assurance

### Package Testing Checklist

- [ ] Installs without errors
- [ ] All dependencies resolved
- [ ] Files in correct locations
- [ ] Executables have correct permissions
- [ ] Configuration files marked as conffiles
- [ ] Service starts correctly (if applicable)
- [ ] Uninstalls cleanly
- [ ] Purge removes all files
- [ ] No lintian errors
- [ ] Man pages present and correct
- [ ] Documentation included

### Testing Commands

```bash
# Install test
sudo dpkg -i package.deb
sudo apt install -f  # Fix dependencies

# File placement
dpkg -L packagename

# Configuration files
dpkg-query -W -f='${Conffiles}\n' packagename

# Removal test
sudo apt remove packagename
dpkg -l | grep packagename  # Should show 'rc' (removed, config remains)

# Purge test
sudo apt purge packagename
dpkg -l | grep packagename  # Should be gone

# Reinstall test
sudo apt install packagename
```

### Automated Testing

**autopkgtest** - Automatic package testing:

```bash
# Install
sudo apt install autopkgtest

# Test package
autopkgtest package.deb -- null

# Test with dependencies
autopkgtest package.deb -- schroot bookworm
```

---

## 15. Distribution Development

### Creating Your Distribution

**Essential components**:

1. **Base system** - Debian packages
2. **Custom packages** - Your modifications
3. **Repository** - Host your packages
4. **Installer** - Install system (Calamares, Debian Installer)
5. **Live system** - Bootable ISO
6. **Documentation** - User guides

### Tools for Distribution Building

#### **live-build**

Create live/installable ISOs:

```bash
# Install
sudo apt install live-build

# Create build directory
mkdir youros-live
cd youros-live

# Configure
lb config --distribution bookworm \
          --debian-installer live \
          --archive-areas "main contrib non-free non-free-firmware" \
          --bootappend-live "boot=live components quiet splash"

# Customize
echo "youros-desktop" >> config/package-lists/desktop.list.chroot
echo "youros-themes" >> config/package-lists/desktop.list.chroot

# Build
sudo lb build

# Result: live-image-amd64.hybrid.iso
```

#### **debootstrap**

Create minimal Debian system:

```bash
# Install
sudo apt install debootstrap

# Create system
sudo debootstrap --arch=amd64 bookworm /mnt/youros http://deb.debian.org/debian

# Chroot into it
sudo chroot /mnt/youros

# Customize from inside
apt update
apt install youros-desktop
```

---

## 16. Key Commands Summary

### Package Management
```bash
# Query installed packages
dpkg -l
dpkg -l | grep pattern
dpkg -S /path/to/file        # Which package owns file
dpkg -L packagename          # List files in package

# Install/remove
sudo dpkg -i package.deb
sudo dpkg -r packagename
sudo dpkg -P packagename     # Purge

# Package info
dpkg-deb -I package.deb
dpkg-deb -c package.deb      # List contents

# APT
sudo apt update
sudo apt upgrade
sudo apt install packagename
sudo apt remove packagename
sudo apt autoremove
apt search keyword
apt show packagename
```

### Package Building
```bash
# Build package
dpkg-buildpackage -us -uc -b

# Check package
lintian package.deb

# Source package
dpkg-source -b directory/
apt-get source packagename
```

### Repository Management
```bash
# Create simple repo
dpkg-scanpackages pool/ /dev/null | gzip > Packages.gz

# reprepro
reprepro includedeb dist package.deb
reprepro list dist
reprepro remove dist packagename
```

### Alternatives
```bash
update-alternatives --config editor
update-alternatives --display editor
update-alternatives --list editor
```

### Debconf
```bash
debconf-show packagename
sudo dpkg-reconfigure packagename
debconf-get-selections
debconf-set-selections < file
```

---

## 17. Resources and Documentation

### Official Debian Documentation

- **Debian Policy Manual**: https://www.debian.org/doc/debian-policy/
- **Debian Developer's Reference**: https://www.debian.org/doc/manuals/developers-reference/
- **Debian New Maintainers' Guide**: https://www.debian.org/doc/manuals/maint-guide/
- **Debian Administrator's Handbook**: https://debian-handbook.info/

### Package Building Guides

- **dh_make tutorial**: `/usr/share/doc/dh-make/`
- **debhelper documentation**: `man debhelper`
- **dpkg documentation**: `man dpkg-deb`, `man dpkg-buildpackage`

### Testing

- **Lintian tags**: https://lintian.debian.org/tags.html
- **Autopkgtest**: https://wiki.debian.org/ContinuousIntegration/autopkgtest

---

## 18. Next Steps for Your OS

### Immediate Actions

1. **Set up development environment**
   ```bash
   sudo apt install build-essential devscripts debhelper dh-make
   ```

2. **Create your first package**
   - Start with a simple metapackage
   - Package your custom theme or wallpaper

3. **Set up repository**
   - Use reprepro for easy management
   - Sign with GPG key

4. **Test thoroughly**
   - Use pbuilder for clean builds
   - Run lintian on all packages

### Medium-term Goals

1. **Build package collection**
   - Desktop metapackage
   - Themes and artwork
   - Configuration packages
   - Custom applications

2. **Create live ISO**
   - Use live-build
   - Test in VMs
   - Refine package selection

3. **Documentation**
   - Installation guide
   - User manual
   - Development documentation

### Long-term Vision

1. **Community building**
   - Release your OS
   - Gather feedback
   - Build contributor base

2. **Maintenance**
   - Security updates
   - Bug fixes
   - Feature additions

3. **Infrastructure**
   - Website
   - Bug tracker
   - Forum/support channels

---

## Quick Reference Card

### Essential Files

| File | Purpose |
|------|---------|
| `/etc/apt/sources.list` | Repository sources |
| `/etc/apt/sources.list.d/` | Additional repositories |
| `/var/lib/dpkg/status` | Installed packages database |
| `/var/cache/apt/archives/` | Downloaded .deb files |
| `/etc/apt/preferences` | Package pinning |
| `/etc/alternatives/` | Alternatives system |

### Package States

| Code | State | Meaning |
|------|-------|---------|
| `ii` | Installed | Installed OK |
| `rc` | Removed | Removed, config remains |
| `un` | Unknown | Not installed |
| `iU` | Installed | Unpacked but not configured |
| `iF` | Half-installed | Installation failed |

### Priority Meanings

| Priority | Auto-install | Purpose |
|----------|--------------|---------|
| required | Yes | Essential for system |
| important | Yes | Important utilities |
| standard | Yes (default) | Standard system |
| optional | No | Optional packages |
| extra | No | Specialized packages |

---

This completes the Debian-Specific Knowledge guide. You now have comprehensive coverage of:
- Debian package system (.deb format)
- APT package management
- Debian Policy requirements
- Alternatives system
- Debconf configuration management
- Repository creation and management
- Package building workflow
- Distribution development

**Ready to practice?** I recommend starting with creating a simple metapackage for your OS that depends on existing Debian packages. This will give you hands-on experience with the package building process without needing to write complex software first.