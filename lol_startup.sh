#!/bin/sh
DIRECTORY=`dirname $0`

/usr/bin/killall -9 /usr/bin/python2.7
$DIRECTORY/fantup.sh &
$DIRECTORY/fastup.sh &
$DIRECTORY/midtub.sh &
$DIRECTORY/shitup.sh &
$DIRECTORY/svd.sh &
