#!/bin/bash

./basic.sh

# Text analysis

./extract-text.sh
./extract-term.sh

# By category tag processing

./extract-marked.sh

# Other

./extract-face.sh

# Statistics

./extract-tag.sh
./extract-msg.sh
./extract-log.sh
./plot-all.sh

echo "Gen topic mining dict"
python gentdict.py

echo "Dump Sqlite to Pickle"
python sqlite2pickle.py

echo "Preprocessing"
python pre.py

echo "Collecting Samples"
python select_samples.py

exit 0 
