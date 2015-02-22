#!/bin/bash

if [ $# -ne 4 ]
then
    echo "Script expects four arguments; an input file name, an output file name, a track number and a track UID." 1>&2
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
python -B "MkvEdit.py" "change_trackuid" "$1" "$2" "$3" "$4"

if [ $? -ne 0 ]
then
    # exit with failure
    destroy_virtualenv
    exit 1
fi

# exit with success
destroy_virtualenv
exit 0
