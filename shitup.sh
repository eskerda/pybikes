#!/bin/sh
DIRECTORY=`dirname $0`
NOT_UPDATE=$1

$DIRECTORY/threader.py system cyclocity all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system velo all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system veloh all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system villo all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system dublin all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system cristolib all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system velostanlib all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system bicloo all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system velocite all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system cyclic all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system tusbic all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system goteborg all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system citycycle all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system velcom all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system mulhouse all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system levelo all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system cergy all 1 $NOT_UPDATE &
#$DIRECTORY/threader.py system vhello all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system velam all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system velov all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system bicikelj all 1 $NOT_UPDATE &
