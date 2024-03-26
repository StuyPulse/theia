#!/bin/bash

ssh samera0 -t "rm -rf theia"
scp -r . samera0:~/theia 2> /dev/null
ssh samera0 -t "systemctl restart theia"