#!/bin/bash

cp access/robot.rsa ~/.ssh/robot.rsa
cp access/robot.rsa.pub ~/.ssh/robot.rsa.pub

scp -oProxyJump=admin@roboRIO-694-FRC.local ~/.ssh/robot.rsa.pub orangepi@samera1:~

cat >> ~/.ssh/config <<EOF

Host samera0
    HostName samera0
    User orangepi
    ProxyJump admin@roboRIO-694-FRC.local
    ForwardAgent true
    IdentityFile ~/.ssh/robot.rsa
EOF
