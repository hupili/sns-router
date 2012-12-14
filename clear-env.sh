#!/bin/bash

# Clear project folder:
#    * '*~' temporary files. 
#    * '*.pyc' compiled files. 

find . -name '*~' | xargs -i rm -f {}
find . -name '*.pyc' | xargs -i rm -f {}

exit 0 
