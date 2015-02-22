"""Contains functions to edit a matroska file."""


from inspect import getmembers, isfunction
from sys import argv, modules


def remove_dateutc(input_filename, output_filename):
    pass


def change_muxingapp(input_filename, output_filename, new_muxingapp):
    pass


def change_writingapp(input_filename, output_filename, new_writingapp):
    pass


def change_trackuid(input_filename, output_filename, track_number, new_trackuid):
    pass


def change_attachment_fileuid(input_filename, output_filename, attachment_filename, new_fileuid):
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
