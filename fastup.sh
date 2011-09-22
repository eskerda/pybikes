#!/bin/sh
DIRECTORY=`dirname $0`
NOT_UPDATE=$1

$DIRECTORY/fast.py system sevici all 3 $NOT_UPDATE &
$DIRECTORY/fast.py system valenbisi all 3 $NOT_UPDATE &
$DIRECTORY/fast.py system velib all 4 $NOT_UPDATE &
