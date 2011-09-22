#!/bin/sh
DIRECTORY=`dirname $0`

/usr/bin/killall -9 /usr/bin/python2.7
$DIRECTORY/fantup.sh > /dev/null &
$DIRECTORY/fastup.sh > /dev/null &
$DIRECTORY/midtub.sh > /dev/null &
$DIRECTORY/shitup.sh > /dev/null &
$DIRECTORY/svd.sh > /dev/null &
