#!/bin/bash

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

ARCH=$(uname -m)
ARCH_NAME=""
if [ "$ARCH" = "aarch64" ]; then
  ARCH_NAME="linuxarm64"
elif [ "$ARCH" = "armv7l" ]; then
  ARCH_NAME="linuxarm32"
elif [ "$ARCH" = "x86_64" ]; then
  ARCH_NAME="linuxx64"
else
  if [ "$#" -ne 1 ]; then
      echo "Can't determine current arch; please provide it (one of):"
      echo ""
      echo "- linuxarm32 (32-bit Linux ARM)"
      echo "- linuxarm64 (64-bit Linux ARM)"
      echo "- linuxx64   (64-bit Linux)"
      exit 1
  else
    echo "Can't detect arch (got $ARCH) -- using user-provided $1"
    ARCH_NAME=$1
  fi
fi

echo "This is the installation script for Theia."
echo "Installing for platform $ARCH_NAME"

echo "Updating existing packages..."
echo "This may take a while..."
apt-get update
apt-get upgrade
echo "Update complete."

echo "Uninstalling existing Python installation"
apt-get remove python3
echo "Python uninstall complete."

echo "Installing python and pip..."
apt-get install python3 python3-pip 
echo "Python and pip installation complete."

echo "Installing v4l-utils..."
apt-get install v4l-utils 
echo "v4l-utils installation complete."

echo "Installing cpufrequtils..."
apt-get install cpufrequtils
echo "cpufrequtils installation complete."

echo "Setting cpufrequtils to performance mode..."
if [ -f /etc/default/cpufrequtils ]; then
    sed -i -e "s/^#\?GOVERNOR=.*$/GOVERNOR=performance/" /etc/default/cpufrequtils
else
    echo "GOVERNOR=\"performance\"" >> /etc/default/cpufrequtils
fi

echo "Installing python dependencies..."
echo "This may take a while..."
pip install numpy 
pip install opencv-contrib-python 
# pip install imutils
pip install robotpy
echo "Python dependencies installation complete."

echo "Downloading Theia..."
mkdir -p /opt/theia
cd /opt/theia
git clone https://github.com/anivanchen/aruco
echo "Download complete."

echo "Creating theia service file..."

if service --status-all | grep -Fq 'theia'; then
  systemctl stop theia
  systemctl disable theia
  rm /lib/systemd/system/theia.service
  rm /etc/systemd/system/theia.service
  systemctl daemon-reload
  systemctl reset-failed
fi

cat > /lib/systemd/system/theia.service <<EOF
[Unit]
Description=Service that runs Theia module

[Service]
WorkingDirectory=/opt/theia
# Run theia at "nice" -10, which is higher priority than standard
Nice=-10
# for non-uniform CPUs, like big.LITTLE, you want to select the big cores
# look up the right values for your CPU
AllowCPUs=4-7

ExecStart=/usr/bin/python3 src/__init__.py
ExecStop=/bin/systemctl kill theia
Type=simple
Restart=on-failure
RestartSec=1

[Install]
WantedBy=multi-user.target
EOF

cp /lib/systemd/system/theia.service /etc/systemd/system/theia.service
chmod 644 /etc/systemd/system/theia.service
systemctl daemon-reload
systemctl enable theia.service
echo "Created and enabled Theia systemd service."

echo "Theia installation successful."
