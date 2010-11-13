HPATH=`pwd`/
DATE=`date`
echo "Starting at "$DATE >> $HPATH"start_log"
python $HPATH"threader.py" system bicing all 1 > /dev/null &
python $HPATH"threader.py" system bizi all 3 > /dev/null &
python $HPATH"threader.py" system cyclocity all 1 > /dev/null &
python $HPATH"threader.py" system sevici all 3 > /dev/null &
python $HPATH"threader.py" system valenbisi all 3 > /dev/null &
python $HPATH"threader.py" system velib all 3 > /dev/null &
python $HPATH"threader.py" system velo all 3 > /dev/null &
python $HPATH"threader.py" system veloh all 3 > /dev/null &
python $HPATH"threader.py" system villo all 3 >/dev/null &
python $HPATH"threader.py" system dublin all 3 > /dev/null &
python $HPATH"threader.py" system cristolib all 3 > /dev/null &
python $HPATH"threader.py" system velostanlib all 2 > /dev/null &
python $HPATH"threader.py" system bicloo all 3 > /dev/null &
python $HPATH"threader.py" system velocite all 2 > /dev/null &
python $HPATH"threader.py" system cyclic all 1 > /dev/null &
python $HPATH"threader.py" system barclays all 1 > /dev/null &
python $HPATH"threader.py" system ecobici all 3 > /dev/null &

python $HPATH"threader.py" system tusbic all 1 > /dev/null &
python $HPATH"threader.py" system goteborg all 1 > /dev/null &
python $HPATH"threader.py" system citycycle all 3 > /dev/null &
python $HPATH"threader.py" system wien all 1 > /dev/null &
python $HPATH"threader.py" system velcom all 1 > /dev/null &
python $HPATH"threader.py" system mulhouse all 1 > /dev/null &
python $HPATH"threader.py" system levelo all 3 > /dev/null &
python $HPATH"threader.py" system cergy all 2 > /dev/null &
python $HPATH"threader.py" system vhello all 1 > /dev/null &
python $HPATH"threader.py" system velam all 1 > /dev/null &

python $HPATH"threader.py" system velov all 5 > /dev/null &
python $HPATH"threader.py" system bixi all 1 > /dev/null &

python $HPATH"threader.py" system melbourne all 1 > /dev/null &
python $HPATH"threader.py" system girocleta all 1 > /dev/null &
