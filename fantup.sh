#!/bin/sh
DIRECTORY=`dirname $0`
NOT_UPDATE=$1

$DIRECTORY/threader.py system barclays all 1  &
$DIRECTORY/threader.py system wien all 1  &
$DIRECTORY/threader.py system bixi all 1  &
$DIRECTORY/threader.py system melbourne all 1  &
$DIRECTORY/threader.py system girocleta all 1  &
$DIRECTORY/threader.py system capitalbikeshare all 1  &
$DIRECTORY/threader.py system decobike all 1  &
$DIRECTORY/threader.py system niceride all 1  &
$DIRECTORY/threader.py system chicago all 1  &
$DIRECTORY/threader.py system denver all 1  &
$DIRECTORY/threader.py system desmoines all 1  &
$DIRECTORY/threader.py system sanantonio all 1  &
$DIRECTORY/threader.py system tobike all 1  &
$DIRECTORY/threader.py system hawaii all 1 &
$DIRECTORY/threader.py system boulder all 1 &
$DIRECTORY/threader.py system bikemi all 1 &
$DIRECTORY/threader.py system ambiciat all 1 &
$DIRECTORY/threader.py system hangzhou populate &
$DIRECTORY/threader.py system mejorenbici all 1 &
$DIRECTORY/threader.py system palma all 1 &
$DIRECTORY/threader.py system bikla all 1 &
