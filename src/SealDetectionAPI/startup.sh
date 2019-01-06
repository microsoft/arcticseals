#!/bin/bash
cd /lf
./Microsoft.LocalForwarder.ConsoleHost noninteractive &
nohup python -m visdom.server &
/usr/bin/supervisord
