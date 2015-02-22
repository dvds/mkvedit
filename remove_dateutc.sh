#!/bin/bash

if [ $# -ne 2 ]
then
    echo "Script expects two arguments; an input file name and an output file name." 1>&2
    exit 1
fi

# where is this script executing?
SCRIPT_DIRECTORY=$(readlink -f "$(dirname "$0")")

pushd "$SCRIPT_DIRECTORY" > /dev/null

# import virtualenv functions
source "virtualenv-functions"

if [ $? -ne 0 ]
then
    echo "Cannot source virtualenv-functions." 1>&2
    exit 1
fi

# exit if virtual environment cannot be created
create_virtualenv_with_pip_requirements
if [ $? -ne 0 ]
then
    exit 1
fi

# execute the python script
python -B "MkvEdit.py" "remove_dateutc" "$1" "$2"

if [ $? -ne 0 ]
then
    # exit with failure
    destroy_virtualenv
    exit 1
fi

# exit with success
destroy_virtualenv
exit 0
