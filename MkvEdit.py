"""Contains functions to edit a matroska file."""


from inspect import getmembers, isfunction
from sys import argv, modules


def remove_dateutc(input_filename, output_filename):
    pass


if __name__ == "__main__":

    if len(argv) < 2:
        raise Exception("Script expects at least a single argument representing the edit command.")

    # does this script contain the requested command?
    command_name = argv[1]
    command_tuples = getmembers(modules[__name__], lambda member: isfunction(member) and member.__name__ == command_name) 

    if len(command_tuples) == 0:
        raise Exception("Cannot find function %s." % command_name)

    # invoke the requested command
    command = command_tuples[0][1]
    arguments = argv[2:]
    command(*arguments)