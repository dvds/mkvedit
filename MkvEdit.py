"""Contains functions to edit a matroska file."""


from inspect import getmembers, isclass, isfunction
from os import SEEK_SET
from sys import argv, modules


from ebml.core import encode_element_id, encode_element_size, encode_unicode_string, read_element_id, read_element_size
from ebml.schema.matroska import DateUTCElement, InfoElement, MatroskaDocument, MuxingAppElement, SegmentElement, WritingAppElement


def remove_dateutc(input_filename, output_filename):

    with open(input_filename, "rb") as input_file:

        with open(output_filename, "wb") as output_file:

            input_matroska_document = MatroskaDocument(input_file)

            offset = 0

            for root_element in input_matroska_document.roots:
                if root_element.id != SegmentElement.id:
                    offset += __write_element(output_file, root_element)

                else:
                    segment_element = root_element

                    dateutc_element_size = 0

                    for segment_child_element in segment_element.value:
                        if segment_child_element.id == InfoElement.id:
                            info_element = segment_child_element

                            for info_child_element in info_element.value:
                                if info_child_element.id == DateUTCElement.id:
                                    dateutc_element = info_child_element

                                    dateutc_element_size = dateutc_element.size

                    offset += __write_element_header(input_file, offset, output_file, segment_element.body_size - dateutc_element_size)

                    for segment_child_element in segment_element.value:
                        if segment_child_element.id != InfoElement.id:
                            offset += __write_element(output_file, segment_child_element)

                        else:
                            info_element = segment_child_element

                            offset += __write_element_header(input_file, offset, output_file, info_element.body_size - dateutc_element_size)

                            for info_child_element in info_element.value:
                                if info_child_element.id != DateUTCElement.id:
                                    offset += __write_element(output_file, info_child_element)


def change_muxingapp(input_filename, output_filename, new_muxingapp):

    with open(input_filename, "rb") as input_file:

        with open(output_filename, "wb") as output_file:

            input_matroska_document = MatroskaDocument(input_file)

            offset = 0

            for root_element in input_matroska_document.roots:
                if root_element.id != SegmentElement.id:
                    offset += __write_element(output_file, root_element)

                else:
                    segment_element = root_element

                    muxingapp_element_body_size = 0

                    for segment_child_element in segment_element.value:
                        if segment_child_element.id == InfoElement.id:
                            info_element = segment_child_element

                            for info_child_element in info_element.value:
                                if info_child_element.id == MuxingAppElement.id:
                                    muxingapp_element = info_child_element

                                    muxingapp_element_body_size = muxingapp_element.body_size

                    offset += __write_element_header(input_file, offset, output_file, segment_element.body_size - (muxingapp_element_body_size - len(new_muxingapp)))

                    for segment_child_element in segment_element.value:
                        if segment_child_element.id != InfoElement.id:
                            offset += __write_element(output_file, segment_child_element)

                        else:
                            info_element = segment_child_element

                            offset += __write_element_header(input_file, offset, output_file, info_element.body_size - (muxingapp_element_body_size - len(new_muxingapp)))

                            for info_child_element in info_element.value:
                                if info_child_element.id != MuxingAppElement.id:
                                    offset += __write_element(output_file, info_child_element)

                                else:
                                    offset += __write_element_header(input_file, offset, output_file, len(new_muxingapp))
                                    offset += __write_element_utf8string(output_file, new_muxingapp)


def change_writingapp(input_filename, output_filename, new_writingapp):

    with open(input_filename, "rb") as input_file:

        with open(output_filename, "wb") as output_file:

            input_matroska_document = MatroskaDocument(input_file)

            offset = 0

            for root_element in input_matroska_document.roots:
                if root_element.id != SegmentElement.id:
                    offset += __write_element(output_file, root_element)

                else:
                    segment_element = root_element

                    writingapp_element_body_size = 0

                    for segment_child_element in segment_element.value:
                        if segment_child_element.id == InfoElement.id:
                            info_element = segment_child_element

                            for info_child_element in info_element.value:
                                if info_child_element.id == WritingAppElement.id:
                                    writingapp_element = info_child_element

                                    writingapp_element_body_size = writingapp_element.body_size

                    offset += __write_element_header(input_file, offset, output_file, segment_element.body_size - (writingapp_element_body_size - len(new_writingapp)))

                    for segment_child_element in segment_element.value:
                        if segment_child_element.id != InfoElement.id:
                            offset += __write_element(output_file, segment_child_element)

                        else:
                            info_element = segment_child_element

                            offset += __write_element_header(input_file, offset, output_file, info_element.body_size - (writingapp_element_body_size - len(new_writingapp)))

                            for info_child_element in info_element.value:
                                if info_child_element.id != WritingAppElement.id:
                                    offset += __write_element(output_file, info_child_element)

                                else:
                                    offset += __write_element_header(input_file, offset, output_file, len(new_writingapp))
                                    offset += __write_element_utf8string(output_file, new_writingapp)


def change_trackuid(input_filename, output_filename, track_number, new_trackuid):
    pass


def change_attachment_fileuid(input_filename, output_filename, attachment_filename, new_fileuid):
    pass


def __write_element(file, element):

    element.stream.seek(0)

    file.write(element.stream.read(element.stream.size))

    return element.stream.size


def __write_element_header(input_file, input_offset, output_file, element_body_size):

    input_file.seek(input_offset, SEEK_SET)

    element_id, element_id_size = read_element_id(input_file)
    element_size, element_size_size = read_element_size(input_file)

    output_offset = output_file.tell()
    output_file.write(encode_element_id(element_id))
    output_file.write(encode_element_size(element_body_size, element_size_size))
    new_output_offset = output_file.tell()

    return new_output_offset - output_offset


def __write_element_utf8string(output_file, value):

    output_offset = output_file.tell()
    output_file.write(encode_unicode_string(value))
    new_output_offset = output_file.tell()

    return new_output_offset - output_offset


if __name__ == "__main__":

    if len(argv) < 2:
        raise Exception("Script expects at least a single argument representing the edit command.")

    # does this script contain the requested command?
    command_name = argv[1]
    command_tuples = getmembers(modules[__name__], lambda member: isfunction(member) and member.__name__ == command_name)

    if len(command_tuples) == 0:
        raise Exception("Cannot find command %s." % command_name)

    # invoke the requested command
    command = command_tuples[0][1]
    arguments = argv[2:]
    command(*arguments)
