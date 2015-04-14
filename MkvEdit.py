"""Contains functions to edit a matroska file."""


from collections import namedtuple
from inspect import getmembers, isfunction
from os import SEEK_CUR
from sys import argv, modules


from ebml.core import encode_element_id, encode_element_size, encode_unicode_string, encode_unsigned_integer, MAXIMUM_ELEMENT_SIZE_LENGTH
from ebml.schema.matroska import AttachmentsElement, AttachedFileElement, DateUTCElement, FileNameElement, FileUIDElement, InfoElement, MatroskaDocument, MuxingAppElement, SegmentElement, TracksElement, TrackEntryElement, TrackNumberElement, TrackUIDElement, WritingAppElement


def remove_dateutc(input_filename, output_filename):

    with open(input_filename, "rb") as input_file:

        input_matroska_document = MatroskaDocument(input_file)

        # retrieve element metadata
        segment_element_metadata = __find_element_metadata(input_matroska_document.roots, SegmentElement, 0)

        info_element_metadata = __find_element_metadata(segment_element_metadata.element.value, InfoElement, segment_element_metadata.offset + segment_element_metadata.element.head_size)

        dateutc_element_metadata = __find_element_metadata(info_element_metadata.element.value, DateUTCElement, info_element_metadata.offset + info_element_metadata.element.head_size)

        # calculate edited element sizes
        new_info_element_body_size = info_element_metadata.element.body_size - dateutc_element_metadata.element.stream.size
        new_info_element_head_size = len(encode_element_size(new_info_element_body_size)) + 4	# 4 byte element id (0x1549A966)

        new_segment_element_body_size = segment_element_metadata.element.body_size + new_info_element_head_size + new_info_element_body_size - info_element_metadata.element.stream.size
        new_segment_element_head_size = len(encode_element_size(new_segment_element_body_size)) + 4	# 4 byte element id (0x18538067)

        # write out the new file
        with open(output_filename, "wb") as output_file:

            # write the pre-segment header block
            input_file.seek(0)
            __buffered_file_copy(input_file, output_file, segment_element_metadata.offset)

            # write the segment header
            output_file.write(encode_element_id(SegmentElement.id))
            output_file.write(encode_element_size(new_segment_element_body_size, MAXIMUM_ELEMENT_SIZE_LENGTH))

            # write the post-segment header block / pre-info header block
            input_file.seek(segment_element_metadata.element.head_size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file, info_element_metadata.offset - (segment_element_metadata.offset + segment_element_metadata.element.head_size))

            # write the info header
            output_file.write(encode_element_id(InfoElement.id))
            output_file.write(encode_element_size(new_info_element_body_size))

            # write the post-info header block / pre-dateutc header block
            input_file.seek(info_element_metadata.element.head_size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file, dateutc_element_metadata.offset - (info_element_metadata.offset + info_element_metadata.element.head_size))

            # write the post-dateutc block
            input_file.seek(dateutc_element_metadata.element.stream.size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file)

            return       


def change_muxingapp(input_filename, output_filename, new_muxingapp):

    with open(input_filename, "rb") as input_file:

        input_matroska_document = MatroskaDocument(input_file)

        # retrieve element metadata
        segment_element_metadata = __find_element_metadata(input_matroska_document.roots, SegmentElement, 0)

        info_element_metadata = __find_element_metadata(segment_element_metadata.element.value, InfoElement, segment_element_metadata.offset + segment_element_metadata.element.head_size)

        muxingapp_element_metadata = __find_element_metadata(info_element_metadata.element.value, MuxingAppElement, info_element_metadata.offset + info_element_metadata.element.head_size)

        # calculate edited element sizes
        new_muxingapp_element_body_size = len(encode_unicode_string(new_muxingapp))
        new_muxingapp_element_head_size = len(encode_element_size(new_muxingapp_element_body_size)) + 2	# 2 byte element id (0x4D80)

        new_info_element_body_size = info_element_metadata.element.body_size + new_muxingapp_element_head_size + new_muxingapp_element_body_size - muxingapp_element_metadata.element.stream.size
        new_info_element_head_size = len(encode_element_size(new_info_element_body_size)) + 4	# 4 byte element id (0x1549A966)

        new_segment_element_body_size = segment_element_metadata.element.body_size + new_info_element_head_size + new_info_element_body_size - info_element_metadata.element.stream.size
        new_segment_element_head_size = len(encode_element_size(new_segment_element_body_size)) + 4	# 4 byte element id (0x18538067)

        # write out the new file
        with open(output_filename, "wb") as output_file:

            # write the pre-segment header block
            input_file.seek(0)
            __buffered_file_copy(input_file, output_file, segment_element_metadata.offset)

            # write the segment header
            output_file.write(encode_element_id(SegmentElement.id))
            output_file.write(encode_element_size(new_segment_element_body_size, MAXIMUM_ELEMENT_SIZE_LENGTH))

            # write the post-segment header block / pre-info header block
            input_file.seek(segment_element_metadata.element.head_size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file, info_element_metadata.offset - (segment_element_metadata.offset + segment_element_metadata.element.head_size))

            # write the info header
            output_file.write(encode_element_id(InfoElement.id))
            output_file.write(encode_element_size(new_info_element_body_size))

            # write the post-info header block / pre-muxingapp header block
            input_file.seek(info_element_metadata.element.head_size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file, muxingapp_element_metadata.offset - (info_element_metadata.offset + info_element_metadata.element.head_size))

            # write the muxingapp header
            output_file.write(encode_element_id(MuxingAppElement.id))
            output_file.write(encode_element_size(new_muxingapp_element_body_size))

            # write the muxingapp
            output_file.write(encode_unicode_string(new_muxingapp))

            # write the post-muxingapp block
            input_file.seek(muxingapp_element_metadata.element.stream.size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file)

            return       


def change_writingapp(input_filename, output_filename, new_writingapp):

    with open(input_filename, "rb") as input_file:

        input_matroska_document = MatroskaDocument(input_file)

        # retrieve element metadata
        segment_element_metadata = __find_element_metadata(input_matroska_document.roots, SegmentElement, 0)

        info_element_metadata = __find_element_metadata(segment_element_metadata.element.value, InfoElement, segment_element_metadata.offset + segment_element_metadata.element.head_size)

        writingapp_element_metadata = __find_element_metadata(info_element_metadata.element.value, WritingAppElement, info_element_metadata.offset + info_element_metadata.element.head_size)

        # calculate edited element sizes
        new_writingapp_element_body_size = len(encode_unicode_string(new_writingapp))
        new_writingapp_element_head_size = len(encode_element_size(new_writingapp_element_body_size)) + 2	# 2 byte element id (0x5741)

        new_info_element_body_size = info_element_metadata.element.body_size + new_writingapp_element_head_size + new_writingapp_element_body_size - writingapp_element_metadata.element.stream.size
        new_info_element_head_size = len(encode_element_size(new_info_element_body_size)) + 4	# 4 byte element id (0x1549A966)

        new_segment_element_body_size = segment_element_metadata.element.body_size + new_info_element_head_size + new_info_element_body_size - info_element_metadata.element.stream.size
        new_segment_element_head_size = len(encode_element_size(new_segment_element_body_size)) + 4	# 4 byte element id (0x18538067)

        # write out the new file
        with open(output_filename, "wb") as output_file:

            # write the pre-segment header block
            input_file.seek(0)
            __buffered_file_copy(input_file, output_file, segment_element_metadata.offset)

            # write the segment header
            output_file.write(encode_element_id(SegmentElement.id))
            output_file.write(encode_element_size(new_segment_element_body_size, MAXIMUM_ELEMENT_SIZE_LENGTH))

            # write the post-segment header block / pre-info header block
            input_file.seek(segment_element_metadata.element.head_size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file, info_element_metadata.offset - (segment_element_metadata.offset + segment_element_metadata.element.head_size))

            # write the info header
            output_file.write(encode_element_id(InfoElement.id))
            output_file.write(encode_element_size(new_info_element_body_size))

            # write the post-info header block / pre-writingapp header block
            input_file.seek(info_element_metadata.element.head_size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file, writingapp_element_metadata.offset - (info_element_metadata.offset + info_element_metadata.element.head_size))

            # write the writingapp header
            output_file.write(encode_element_id(WritingAppElement.id))
            output_file.write(encode_element_size(new_writingapp_element_body_size))

            # write the writingapp
            output_file.write(encode_unicode_string(new_writingapp))

            # write the post writingapp block
            input_file.seek(writingapp_element_metadata.element.stream.size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file)

            return       


def change_trackuid(input_filename, output_filename, track_number, new_trackuid):

    with open(input_filename, "rb") as input_file:

        input_matroska_document = MatroskaDocument(input_file)

        # retrieve element metadata
        segment_element_metadata = __find_element_metadata(input_matroska_document.roots, SegmentElement, 0)

        tracks_element_metadata = __find_element_metadata(segment_element_metadata.element.value, TracksElement, segment_element_metadata.offset + segment_element_metadata.element.head_size)

        trackentry_element_metadata = __find_element_metadata(tracks_element_metadata.element.value, TrackEntryElement, tracks_element_metadata.offset + tracks_element_metadata.element.head_size, lambda e: e.id == TrackNumberElement.id and e.value == long(track_number))

        trackuid_element_metadata = __find_element_metadata(trackentry_element_metadata.element.value, TrackUIDElement, trackentry_element_metadata.offset + trackentry_element_metadata.element.head_size)

        # calculate edited element sizes
        new_trackuid_element_body_size = len(encode_unsigned_integer(long(new_trackuid)))
        new_trackuid_element_head_size = len(encode_element_size(new_trackuid_element_body_size)) + 2	# 2 byte element id (0x73C5)

        new_trackentry_element_body_size = trackentry_element_metadata.element.body_size + new_trackuid_element_head_size + new_trackuid_element_body_size - trackuid_element_metadata.element.stream.size
        new_trackentry_element_head_size = len(encode_element_size(new_trackentry_element_body_size)) + 1	# 1 byte element id (0xAE)

        new_tracks_element_body_size = tracks_element_metadata.element.body_size + new_trackentry_element_head_size + new_trackentry_element_body_size - trackentry_element_metadata.element.stream.size
        new_tracks_element_head_size = len(encode_element_size(new_tracks_element_body_size)) + 4	# 4 byte element id (0x1654AE6B)

        new_segment_element_body_size = segment_element_metadata.element.body_size + new_tracks_element_head_size + new_tracks_element_body_size - tracks_element_metadata.element.stream.size
        new_segment_element_head_size = len(encode_element_size(new_segment_element_body_size)) + 4	# 4 byte element id (0x18538067)

        # write out the new file
        with open(output_filename, "wb") as output_file:

            # write the pre-segment header block
            input_file.seek(0)
            __buffered_file_copy(input_file, output_file, segment_element_metadata.offset)

            # write the segment header
            output_file.write(encode_element_id(SegmentElement.id))
            output_file.write(encode_element_size(new_segment_element_body_size, MAXIMUM_ELEMENT_SIZE_LENGTH))

            # write the post-segment header block / pre-tracks header block
            input_file.seek(segment_element_metadata.element.head_size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file, tracks_element_metadata.offset - (segment_element_metadata.offset + segment_element_metadata.element.head_size))

            # write the tracks header
            output_file.write(encode_element_id(TracksElement.id))
            output_file.write(encode_element_size(new_tracks_element_body_size))

            # write the post-tracks header block / pre-trackentry header block
            input_file.seek(tracks_element_metadata.element.head_size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file, trackentry_element_metadata.offset - (tracks_element_metadata.offset + tracks_element_metadata.element.head_size))

            # write the trackentry header
            output_file.write(encode_element_id(TrackEntryElement.id))
            output_file.write(encode_element_size(new_trackentry_element_body_size))

            # write the post-trackentry header block / pre-trackuid header block
            input_file.seek(trackentry_element_metadata.element.head_size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file, trackuid_element_metadata.offset - (trackentry_element_metadata.offset + trackentry_element_metadata.element.head_size))

            # write the trackuid header
            output_file.write(encode_element_id(TrackUIDElement.id))
            output_file.write(encode_element_size(new_trackuid_element_body_size))

            # write the trackuid
            output_file.write(encode_unsigned_integer(long(new_trackuid)))

            # write the post trackuid block
            input_file.seek(trackuid_element_metadata.element.stream.size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file)

            return       


def change_attachment_fileuid(input_filename, output_filename, attachment_filename, new_fileuid):

    with open(input_filename, "rb") as input_file:

        input_matroska_document = MatroskaDocument(input_file)

        # retrieve element metadata
        segment_element_metadata = __find_element_metadata(input_matroska_document.roots, SegmentElement, 0)

        attachments_element_metadata = __find_element_metadata(segment_element_metadata.element.value, AttachmentsElement, segment_element_metadata.offset + segment_element_metadata.element.head_size)

        attachedfile_element_metadata = __find_element_metadata(attachments_element_metadata.element.value, AttachedFileElement, attachments_element_metadata.offset + attachments_element_metadata.element.head_size, lambda e: e.id == FileNameElement.id and e.value == attachment_filename)

        fileuid_element_metadata = __find_element_metadata(attachedfile_element_metadata.element.value, FileUIDElement, attachedfile_element_metadata.offset + attachedfile_element_metadata.element.head_size)

        # calculate edited element sizes
        new_fileuid_element_body_size = len(encode_unsigned_integer(long(new_fileuid)))
        new_fileuid_element_head_size = len(encode_element_size(new_fileuid_element_body_size)) + 2	# 2 byte element id (0x46AE)

        new_attachedfile_element_body_size = attachedfile_element_metadata.element.body_size + new_fileuid_element_head_size + new_fileuid_element_body_size - fileuid_element_metadata.element.stream.size
        new_attachedfile_element_head_size = len(encode_element_size(new_attachedfile_element_body_size)) + 2	# 2 byte element id (0x61A7)

        new_attachments_element_body_size = attachments_element_metadata.element.body_size + new_attachedfile_element_head_size + new_attachedfile_element_body_size - attachedfile_element_metadata.element.stream.size
        new_attachments_element_head_size = len(encode_element_size(new_attachments_element_body_size)) + 4	# 4 byte element id (0x1941A469)

        new_segment_element_body_size = segment_element_metadata.element.body_size + new_attachments_element_head_size + new_attachments_element_body_size - attachments_element_metadata.element.stream.size
        new_segment_element_head_size = len(encode_element_size(new_segment_element_body_size)) + 4	# 4 byte element id (0x18538067)

        # write out the new file
        with open(output_filename, "wb") as output_file:

            # write the pre-segment header block
            input_file.seek(0)
            __buffered_file_copy(input_file, output_file, segment_element_metadata.offset)

            # write the segment header
            output_file.write(encode_element_id(SegmentElement.id))
            output_file.write(encode_element_size(new_segment_element_body_size, MAXIMUM_ELEMENT_SIZE_LENGTH))

            # write the post-segment header block / pre-attachments header block
            input_file.seek(segment_element_metadata.element.head_size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file, attachments_element_metadata.offset - (segment_element_metadata.offset + segment_element_metadata.element.head_size))

            # write the attachments header
            output_file.write(encode_element_id(AttachmentsElement.id))
            output_file.write(encode_element_size(new_attachments_element_body_size))

            # write the post-attachments header block / pre-attachedfile header block
            input_file.seek(attachments_element_metadata.element.head_size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file, attachedfile_element_metadata.offset - (attachments_element_metadata.offset + attachments_element_metadata.element.head_size))

            # write the attachedfile header
            output_file.write(encode_element_id(AttachedFileElement.id))
            output_file.write(encode_element_size(new_attachedfile_element_body_size))

            # write the post-attachedfile header block / pre-fileuid header block
            input_file.seek(attachedfile_element_metadata.element.head_size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file, fileuid_element_metadata.offset - (attachedfile_element_metadata.offset + attachedfile_element_metadata.element.head_size))

            # write the fileuid header
            output_file.write(encode_element_id(FileUIDElement.id))
            output_file.write(encode_element_size(new_fileuid_element_body_size))

            # write the fileuid
            output_file.write(encode_unsigned_integer(long(new_fileuid)))

            # write the post fileuid block
            input_file.seek(fileuid_element_metadata.element.stream.size, SEEK_CUR)
            __buffered_file_copy(input_file, output_file)

            return       


def __find_element_metadata(element_list, find_element, starting_offset, child_element_predicate = None):

    ElementMetadata = namedtuple('ElementMetadata', 'element offset')

    offset = starting_offset

    # enumerate the elements in the list until the requested element is found...
    for element in element_list:
        if element.id != find_element.id:
            offset += element.stream.size

        else:
            if child_element_predicate is None:
                # ...no predicate so just return it with the starting offset
                return ElementMetadata(element, offset)

            else:
                # ....then evaluate the predicate and on matching return it with the starting offset
                for child_element in element.value:
                    if child_element_predicate(child_element):
                        return ElementMetadata(element, offset)

                    else:
                        offset += element.stream.size
                        break

    raise Exception("No {0} element found.".format(find_element.name))


def __buffered_file_copy(input_file, output_file, number_of_bytes = None):

    # copy the input file piece-by-piece to avoid excessive memory use
    for data in __yielding_read(input_file, number_of_bytes):
        output_file.write(data)


def __yielding_read(file_object, number_of_bytes = None):

    DEFAULT_CHUNK_SIZE = 1024 * 64	# 64kb
    accumulator = 0

    while (number_of_bytes is None) or (number_of_bytes is not None and accumulator < number_of_bytes):

        # calculate the chunk size to use
        chunk_size = DEFAULT_CHUNK_SIZE
        if number_of_bytes is not None and ((number_of_bytes - accumulator) < DEFAULT_CHUNK_SIZE):
            chunk_size = (number_of_bytes - accumulator)

        # read data and break if EOF reached
        data = file_object.read(chunk_size)
        if not data:
            break

        # advance accumulator and yield data
        accumulator += len(data)
        yield data


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
