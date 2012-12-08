#!/bin/bash
# Extract single page pictures from slides. 

pdftk presentation-white.pdf cat 2 output ../pic/sns-het.pdf
pdftk presentation-white.pdf cat 4 output ../pic/snsapi-arch.pdf
pdftk presentation-white.pdf cat 5 output ../pic/snsapi-screen-1.pdf
pdftk presentation-white.pdf cat 8 output ../pic/srfe-screen-1.pdf
pdftk presentation-white.pdf cat 9 output ../pic/srfe-screen-2.pdf
pdftk presentation-white.pdf cat 11 output ../pic/graph-induction.pdf

exit 0 
