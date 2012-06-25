#!/bin/sh
DIRECTORY=`dirname $0`
NOT_UPDATE=$1

$DIRECTORY/threader.py system sevici all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system valenbisi all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system velib all 1 $NOT_UPDATE &
