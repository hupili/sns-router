#!/bin/bash
#Plot histogram

if [[ $# != 2 ]] ; then
	echo "usage: $0 {fn_data} {fn_output}"
else
	fn_data=$1
	fn_output=$2
	#fn_temp_prefix=$3
fi

#temp=plot/plot.t.html
#embed="cat plot/plot.t.html.front - plot/plot.t.html.end"

temp="plot/hist.t.html"
embed="cat $temp.front - $temp.end"

cat $fn_data | awk '{printf("[\"%s\",%d],",$2, $1)}' | $embed > $fn_output

chmod o+r $fn_output

exit 0 
