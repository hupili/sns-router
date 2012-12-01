#!/bin/bash

./basic.sh

# Text analysis

./extract-text.sh
./extract-term.sh
./extract-marked-term.sh

# Other

./extract-face.sh

# Statistics

./extract-tag.sh
./extract-msg.sh
./extract-log.sh
./plot-all.sh

exit 0 
