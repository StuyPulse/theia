#!/bin/bash

:'
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
'

if ! command -v sshpass &> /dev/null
    # mac install: brew install hudochenkov/sshpass/sshpass

    sshpass -porangepi scp -r . orangepi@orangepi5:~/theia
    echo "--- RESTARTING THEIA SERVICE ---"
    sshpass -porangepi ssh orangepi@orangepi5 -t "systemctl restart theia"
then
    echo "sshpass could not be found, using ssh"

    scp -r . orangepi@orangepi5:~/theia
    echo "--- RESTARTING THEIA SERVICE ---"
    ssh orangepi@orangepi5 -t "systemctl restart theia"

    exit 1
fi
