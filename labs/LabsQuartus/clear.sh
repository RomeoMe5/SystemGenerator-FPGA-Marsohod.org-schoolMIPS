#!/bin/bash
# by hell03end

# Files formats:
#    * .qpf - Quartus II project file
#    * .qsf - settings for Quartus II project
#    * .bdf - file to store block diagram/scheme for elements topology
#    * .vwf - file to store vector waveforms for input signal
#    * .bsf - symbol files for block diagram/scheme (module)
#    * .v   - Verilog HDL file
#    * .sh  - scripting files
#    * .hex - memory dumps
#    * .qip - ip-functions declaration
#    * .csv - pin assignment dumps

set -e
# set -x # debug
# set -v # verbose output

FILES_TO_EXCLUDE_PATTERN=".(vwf|bdf|qpf|qsf|v|sh|bsf|hex|qip|csv)"
# add '..' and '.' special folders
FILES_TO_EXCLUDE_PATTERN="($FILES_TO_EXCLUDE_PATTERN|^(.|..))$"

function show_help {
    echo "remove extra files left from Quartus II exectution"
    echo
    echo "Do not remove: '$FILES_TO_EXCLUDE_PATTERN' files"
    echo "clear.sh [-l]"
    echo "    -l - remove files from current directory (local)"
    echo
}

function remove_files {
    for file in `find . -maxdepth 1 | grep -vE "$FILES_TO_EXCLUDE_PATTERN"`; do
        rm -r $file  # also remove folders
    done
}

for arg in $*; do
    # TODO: use 'in' keyword
    if [ "$arg" = "-h" -o "$arg" = "-H" -o "$arg" = "--help" -o "$arg" = "/?" ]; then
        show_help
        exit
    fi
done

# remove files from current folder
for arg in $*; do
    if [ "$arg" = "-l" ]; then
        remove_files
        exit
    fi
done

for dir in `ls -d */`; do
    # remove files inside dir (non-local)
    cd $dir
    remove_files
    cd ..
done
