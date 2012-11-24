#/bin/bash

embed="cat plot/plot.t.html.front - plot/plot.t.html.end"

cat data/log.flag.tab.f1.time.day-freq | awk '{printf("[\"%s\",%d],",$2, $1)}' | $embed > plot/day-freq.html
cat data/log.flag.tab.f1.time.hour-freq | awk '{printf("[\"%s\",%d],",$2, $1)}' | $embed > plot/hour-freq.html

chmod o+r plot/*.html

exit 0 
