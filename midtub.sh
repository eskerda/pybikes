#!/bin/sh
DIRECTORY=`dirname $0`
NOT_UPDATE=$1

$DIRECTORY/threader.py system ecobici all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system bizi all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system bicing all 4 $NOT_UPDATE &
