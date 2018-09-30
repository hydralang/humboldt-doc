#!/usr/bin/python

from __future__ import print_function

import abc
import math
import sys
import textwrap

import cli_tools
import six
import yaml

leader = [
    "                     1                   2                   3",
    " 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1",
]

boundary = "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"


def _center(width, length):
    return int(math.ceil((width - length) / 2.0))


@six.add_metaclass(abc.ABCMeta)
class AbstractField(object):
    def __init__(self, bits):
        self.bits = bits

    @abc.abstractmethod
    def content(self, lines):
        """
        Retrieve the content of the field.

        :param int lines: The total number of lines to fill.

        :returns: A list ``lines`` elements long, containing text
                  ``self.width`` characters wide.
        """

    @property
    def width(self):
        """
        Retrieve the character width of the field.
        """

        return self.bits * 2 - 1

    @abc.abstractproperty
    def height(self):
        """
        The minimum height of the field.
        """

        pass


class BitField(AbstractField):
    def __init__(self, name):
        super(BitField, self).__init__(1)

        self.name = name

    def content(self, lines):
        if lines < self.height:
            raise Exception(
                'Field too short for "%s" (%d lines provided)' %
                (self.name, lines)
            )

        result = [' '] * _center(lines, self.height)
        result.extend(self.name)
        result.extend([' '] * (lines - len(result)))

        return result

    @property
    def height(self):
        return len(self.name)


class ReservedField(AbstractField):
    height = 1

    def content(self, lines):
        line = ' .' * (self.bits - 1) + ' '
        return [line] * lines


class Field(AbstractField):
    def __init__(self, bits, name):
        super(Field, self).__init__(bits)

        self.name = name

        # Go ahead and word-wrap the text
        text = textwrap.wrap(name, self.width - 2, break_long_words=False)
        if max(len(line) for line in text) > self.width - 2:
            raise Exception(
                "Words too long to fit %d-bit field (%d character width "
                "available)" % (bits, self.width - 2)
            )

        # Add the size if possible
        size = '(%d-bit)' % bits
        if len(size) < self.width - 2:
            text.append(size)

        # Center the text
        self.text = [line.center(self.width) for line in text]

    def content(self, lines):
        if lines < self.height:
            raise Exception(
                'Field to short for "%s" (%d lines provided, %d needed)' %
                (self.name, lines, self.height)
            )

        result = [' ' * self.width] * (_center(lines, self.height) + 1)
        result.extend(self.text)
        result.extend([' ' * self.width] * (lines - len(result)))

        return result

    @property
    def height(self):
        return len(self.text) + 2


@six.add_metaclass(abc.ABCMeta)
class AbstractRow(object):
    @abc.abstractmethod
    def render(self):
        """
        Render the row.

        :returns: A list of lines, including the left and right
                  boundaries, but not the top or bottom boundary.
        """

        pass

    @abc.abstractproperty
    def bits(self):
        """
        The total number of bits represented by the row.
        """

        pass


class Row(AbstractRow):
    bits = 32

    def __init__(self, fields):
        # Verify the number of bits
        bits = sum(f.bits for f in fields)
        if bits != 32:
            raise Exception('Row contains %d bits' % bits)

        # Merge adjacent reserved fields
        self.fields = []
        last_resv = None
        for fld in fields:
            if last_resv:
                if isinstance(fld, ReservedField):
                    last_resv = ReservedField(last_resv.bits + fld.bits)
                    continue
                else:
                    self.fields.append(last_resv)
                    last_resv = None
            elif isinstance(fld, ReservedField):
                last_resv = fld
                continue

            self.fields.append(fld)
        if last_resv:
            self.fields.append(last_resv)

    def render(self):
        # Calculate the required height
        height = max(f.height for f in self.fields)

        # Begin rendering the row
        content = ['|'] * height
        for field in self.fields:
            fld_ctnt = field.content(height)
            assert len(fld_ctnt) == height

            # Add the text to each row
            for i in range(height):
                content[i] += fld_ctnt[i] + '|'

        return content


class MultiRow(AbstractRow):
    # Maximum row width
    WIDTH = 63

    # Maximum text width; provides space for the "- " and " -" at the
    # ends of the center row
    TEXT_WIDTH = WIDTH - 4

    def __init__(self, bits, text):
        # Verify the number of bits
        if bits % 32 != 0:
            raise Exception(
                'MultiRow requires a multiple of 32 bits, not %d' % bits
            )

        # Save the number of bits and the text
        self._bits = bits
        self.text = text

        # Calculate the number of lines
        height = bits / 32 * 2 - 1

        # Word-wrap the text
        text = textwrap.wrap(text, self.TEXT_WIDTH, break_long_words=False)
        width = max(len(line) for line in text)
        if width > self.TEXT_WIDTH:
            raise Exception(
                "Words too long to fit (%d character width available)" %
                self.TEXT_WIDTH
            )
        if len(text) > height - 2:
            raise Exception(
                "Too many lines to fit (%d lines used, %d available)" %
                (len(text), height - 2)
            )

        # Is there space for the size line?
        size = '(%d-bit)' % bits
        if len(text) < height - 2:
            if len(size) < self.TEXT_WIDTH:
                text.append(size)
        elif len(text[-1]) < self.TEXT_WIDTH - len(size) - 1:
            text[-1] += ' %s' % size

        # Surround the text in spaces
        centered = [' ' + line + ' ' for line in text]

        # Construct the base field representation
        self.content = [
            "|" + " " * self.WIDTH + "|",
            "+" + "- " * (self.WIDTH / 2) + "-+",
        ] * (height / 2) + ["|" + " " * self.WIDTH + "|"]

        # Overlay the text
        start = _center(height, len(centered))
        for i in range(start, start + len(centered)):
            idx = _center(self.WIDTH + 2, len(centered[i - start]) + 2)
            self.content[i] = (
                self.content[i][:idx] +
                centered[i - start] +
                self.content[i][idx + len(centered[i - start]):]
            )

    def render(self):
        return self.content

    @property
    def bits(self):
        return self._bits


@six.add_metaclass(abc.ABCMeta)
class AbstractVarWidth(object):
    _UNIT = 'byte'

    def __init__(self, name):
        self.name = name
        self.size = None

    def mkpfx(self, prefix, pointer):
        """
        Construct a pair of prefixes; the first will be the prefix for the
        first line, and the second will be the prefix for subsequent
        lines.

        :param str prefix: A prefix to attach to each line.
        :param str pointer: A specification of the pointer to prefix
                            the line with.  If ``None``, no pointer
                            will be prefixed.

        :returns: A tuple of two prefixes.
        """

        if pointer is None:
            # Simplest case
            return (prefix, prefix)

        if pointer == '|':
            return ('%s+- ' % prefix, '%s|  ' % prefix)

        return ('%s`- ' % prefix, '%s   ' % prefix)

    def set_size(self, size):
        self.size = size

    def render_name(self, width, first, remainder, extra):
        text = (
            '%s%s (%s)' % (
                ('[%s] ' % extra) if extra else '',
                self.name, self.TYPE,
            )
        )

        return textwrap.wrap(
            text, width,
            break_long_words=False,
            initial_indent=first,
            subsequent_indent=remainder,
        )

    @abc.abstractmethod
    def render(self, width, prefix='', pointer=None, extra=None):
        """
        Render the variable width object.

        :param int width: The maximum text width for the rendering.
        :param str prefix: A prefix to attach to each line.
        :param str pointer: A specification of the pointer to prefix
                            the line with.  If ``None``, no pointer
                            will be prefixed.
        :param str extra: Extra text to prepend to the first line.

        :returns: A list of lines containing the rendering of the
                  field, plus any specified prefix.
        """

        pass

    @property
    def TYPE(self):
        if self.size is not None:
            return (
                '%d-%s %s' % (self.size, self._UNIT, self._TYPE)
            )

        return self._TYPE

    @property
    def _TYPE(self):
        return self.__class__.__name__.lower()


class Integer(AbstractVarWidth):
    _UNIT = 'bit'
    _TYPE = 'int'

    def render(self, width, prefix='', pointer=None, extra=None):
        return self.render_name(
            width, *self.mkpfx(prefix, pointer),
            extra=extra
        )

    def set_size(self, size):
        if size % 8 > 0:
            raise Exception('Invalid size %d not a multiple of 8 bits' % size)

        super(Integer, self).set_size(size)


class String(AbstractVarWidth):
    _TYPE = 'str'

    def render(self, width, prefix='', pointer=None, extra=None):
        return self.render_name(
            width, *self.mkpfx(prefix, pointer),
            extra=extra
        )


class Byte(AbstractVarWidth):
    def render(self, width, prefix='', pointer=None, extra=None):
        return self.render_name(
            width, *self.mkpfx(prefix, pointer),
            extra=extra
        )


class List(AbstractVarWidth):
    _UNIT = 'element'

    def __init__(self, name, contents):
        super(List, self).__init__(name)

        self.contents = contents

    def render(self, width, prefix='', pointer=None, extra=None):
        first, remainder = self.mkpfx(prefix, pointer)

        contents = self.render_name(width, first, remainder, extra)
        contents.extend(self.contents.render(width, remainder, '`'))

        return contents


class Struct(AbstractVarWidth):
    def __init__(self, name, contents):
        super(Struct, self).__init__(name)

        self.contents = contents

    def render(self, width, prefix='', pointer=None, extra=None):
        first, remainder = self.mkpfx(prefix, pointer)

        contents = self.render_name(width, first, remainder, extra)
        for i, (key, value) in enumerate(self.contents):
            contents.extend(value.render(
                width, remainder,
                '`' if i + 1 == len(self.contents) else '|',
                key,
            ))

        return contents


class Packet(object):
    _var_fields = ('int', 'str', 'byte', 'list', 'struct')

    @classmethod
    def _var_from_elem(cls, elem):
        if 'int' in elem:
            var = Integer(elem['int'])
        elif 'str' in elem:
            var = String(elem['str'])
        elif 'byte' in elem:
            var = Byte(elem['byte'])
        elif 'list' in elem:
            var = List(elem['list'], cls._var_from_elem(elem['contents']))
        elif 'struct' in elem:
            contents = []
            for item in elem['contents']:
                contents.append((
                    item.get('name'), cls._var_from_elem(item['type']),
                ))

            # Structs can't have a size
            return Struct(elem['struct'], contents)

        if 'size' in elem:
            var.set_size(elem['size'])

        return var

    @classmethod
    def from_yaml(cls, fname):
        with open(fname) as f:
            all_data = list(yaml.safe_load_all(f))

        for data in all_data:
            # Interpret the YAML
            extra = {}
            bit_count = 0
            fields = []
            rows = []
            var_width = []
            for elem in data:
                if 'header' in elem:
                    extra['header'] = elem['header']
                elif 'protocol' in elem:
                    extra['protocol'] = elem['protocol']
                    type_ = ''
                    if elem.get('reply', False):
                        extra['reply'] = True
                        type_ = ' reply'
                    elif elem.get('error', False):
                        extra['error'] = True
                        type_ = ' error'
                    if elem.get('name'):
                        extra['name'] = elem['name']
                        extra['header'] = (
                            '%s (protocol %d%s)' %
                            (elem['name'], elem['protocol'], type_)
                        )
                    else:
                        extra['header'] = (
                            'Protocol %d%s' % (elem['protocol'], type_)
                        )
                elif 'payload' in elem:
                    extra['payload'] = elem['payload']
                elif 'bit' in elem:
                    fields.append(BitField(elem['bit']))
                    bit_count += 1
                elif 'reserved' in elem:
                    bits = elem['reserved']
                    while bit_count + bits > 32:
                        fields.append(ReservedField(32 - bit_count))
                        bits -= 32 - bit_count
                        rows.append(Row(fields))
                        fields = []
                        bit_count = 0
                    fields.append(ReservedField(bits))
                    bit_count += bits
                elif 'field' in elem:
                    name = elem['field']
                    bits = elem['bits']
                    if fields and bits > 32 - bit_count:
                        raise Exception(
                            'Field %s split across 32-bit boundary' % name
                        )
                    if bits > 32:
                        rows.append(MultiRow(bits, name))
                    else:
                        fields.append(Field(bits, name))
                        bit_count += bits
                elif any(x in elem for x in cls._var_fields):
                    var_width.append(cls._var_from_elem(elem))
                else:
                    raise Exception('Unknown field in %s: "%r"' % fname, elem)

                if bit_count >= 32:
                    rows.append(Row(fields))
                    fields = []
                    bit_count = 0

            if bit_count > 0:
                fields.append(ReservedField(32 - bit_count))
                rows.append(Row(fields))

            yield cls(rows, var_width, **extra)

    def __init__(self, rows, var_width, **extra):
        self.rows = rows
        self.var_width = var_width
        self.extra = extra

        self._data = None

    def __getattr__(self, name):
        return self.extra.get(name)

    def render(self, indent=''):
        # Initialize the lines with the leader
        lines = []
        if self.header:
            lines.extend([
                '%s:' % self.header,
            ])
        if self.rows:
            lines.append('')
            lines.extend(leader[:])
            lines.append(boundary)

            # Add each of the rows
            for row in self.rows:
                lines.extend(row.render())
                lines.append(boundary)

        # Offset variable width fields, if present
        if self.var_width or self.payload:
            if self.rows:
                lines.append('')
            lines.append('  Variable width fields:')

        # Render the variable width fields
        for field in self.var_width:
            text = field.render(len(boundary) - 4)
            lines.append('  * ' + text[0])
            lines.extend('    ' + line for line in text[1:])

        # Describe the payload
        if self.payload:
            lines.extend(textwrap.wrap(
                '%s (payload)' % self.payload, len(boundary),
                break_long_words=False,
                initial_indent='  * ',
                subsequent_indent='    ',
            ))

        # Construct and return the final rendered output
        return indent + ('\n' + indent).join(lines)

    def _data_render(self, var):
        result = {
            var._TYPE: var.name,
        }

        # Add the size
        if var.size is not None:
            result['size'] = var.size

        # Add the contents, if any
        if isinstance(var, List):
            result['contents'] = self._data_render(var.contents)
        elif isinstance(var, Struct):
            result['contents'] = []
            for key, value in var.contents:
                item = {'type': self._data_render(value)}
                if key:
                    item['name'] = key
                result['contents'].append(item)

        return result

    @property
    def data(self):
        if self._data is None:
            self._data = []

            # First, set up the header information
            if self.protocol:
                proto = {
                    'protocol': self.protocol,
                }
                if self.name:
                    proto['name'] = self.name
                if self.reply:
                    proto['reply'] = self.reply
                if self.error:
                    proto['error'] = self.error
                self._data.append(proto)
            elif self.header:
                self._data.append({'header': self.header})

            # Next, render the rows
            for row in self.rows:
                if isinstance(row, MultiRow):
                    self._data.append({
                        'field': row.text,
                        'bits': row.bits,
                    })
                else:
                    for field in row.fields:
                        if isinstance(field, BitField):
                            self._data.append({'bit': field.name})
                        elif isinstance(field, ReservedField):
                            if 'reserved' in self._data[-1]:
                                self._data[-1].bits += field.bits
                            else:
                                self._data.append({'reserved': field.bits})
                        elif isinstance(field, Field):
                            self._data.append({
                                'field': field.name,
                                'bits': field.bits,
                            })

            # Now render variable-width fields, if any
            for var in self.var_width:
                self._data.append(self._data_render(var))

            # Finally, render the payload
            if self.payload:
                self._data.append({'payload': self.payload})

        return self._data


@cli_tools.argument(
    'files',
    nargs='+',
    help='The YAML files to render.',
)
@cli_tools.argument(
    '--indent', '-i',
    default='',
    help='The indent to add to the beginning of each line.',
)
@cli_tools.argument(
    '--bare', '-b',
    action='store_true',
    help='Suppress the filename and index header.',
)
@cli_tools.argument(
    '--debug', '-d',
    action='store_true',
    help='Enable debugging output.',
)
def main(files, indent='', bare=False):
    """
    Render a YAML file describing a protocol packet into a textual
    representation of that protocol packet.
    """

    sep = False
    for fname in files:
        for i, packet in enumerate(Packet.from_yaml(fname)):
            if sep:
                print()
            if not bare:
                print('%s%s:\n' % (fname, (' (idx %d)' % i) if i > 0 else ''))
            print(packet.render(indent))
            sep = True


if __name__ == '__main__':
    sys.exit(main.console())
