#/bin/bash

#cat data/log.flag.tab.f1.time.day-freq | awk '{printf("[\"%s\",%d],",$2, $1)}' | $embed > plot/day-freq.html
#cat data/log.flag.tab.f1.time.hour-freq | awk '{printf("[\"%s\",%d],",$2, $1)}' | $embed > plot/hour-freq.html

./plot-hist.sh data/log.flag.tab.f1.time.day-freq plot/flag-day-freq.html
./plot-hist.sh data/log.flag.tab.f1.time.hour-freq plot/flag-hour-freq.html
./plot-hist.sh data/msg.tab.time.day-freq plot/msg-day-freq.html
./plot-hist.sh data/msg.tab.time.hour-freq plot/msg-hour-freq.html

chmod o+r plot/plots.html

exit 0 
