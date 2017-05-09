set term png

set datafile sep ','
set ytic 1

set xdata time

set timefmt '%Y-%m-%dT%H:%M:%S'
set format x "%Y-%m-%dT%H:%M:%S"
set xtics format "%H:%M"
set yrange [-5:5]
plot 'logs.csv' using 1:2
set output 'accesschart.png'
set xrange [GPVAL_X_MIN:GPVAL_X_MAX]
set title 'Access Time Graph'
set ylabel 'Lock state (1 = Unlocked, 0 = Idle, -1 = Deactivated)'
set xlabel 'Time'
plot 'logs.csv' title '' using 1:2 with lines
