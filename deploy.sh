#!/bin/bash

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
