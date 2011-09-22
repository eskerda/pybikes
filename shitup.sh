#!/bin/sh
DIRECTORY=`dirname $0`
NOT_UPDATE=$1

$DIRECTORY/threader.py system cyclocity all 3 $NOT_UPDATE &
$DIRECTORY/threader.py system velo all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system veloh all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system villo all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system dublin all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system cristolib all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system velostanlib all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system bicloo all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system velocite all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system cyclic all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system tusbic all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system goteborg all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system citycycle all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system velcom all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system mulhouse all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system levelo all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system cergy all 2 $NOT_UPDATE &
#$DIRECTORY/threader.py system vhello all 1 $NOT_UPDATE &
$DIRECTORY/threader.py system velam all 2 $NOT_UPDATE &
$DIRECTORY/threader.py system velov all 3 $NOT_UPDATE &
$DIRECTORY/threader.py system bicikelj all 1 $NOT_UPDATE &
