#!/usr/bin/python

from __future__ import print_function

import abc
import os
import shutil
import sys

import cli_tools
import six
import yaml


class PBException(Exception):
    def __init__(self, message, fname=None, lno=None):
        super(PBException, self).__init__(
            '%s:%d: %s' % (fname, lno, message),
        )

        self.fname = fname
        self.lno = lno


@six.add_metaclass(abc.ABCMeta)
class Statement(object):
    @abc.abstractmethod
    def match(cls, parser, lno, line, comment):
        pass

    def __init__(self, fname, lno):
        self.fname = fname
        self.lno = lno

    @abc.abstractmethod
    def render(self, lno, store, pfx=''):
        pass


class Container(object):
    def _list(self, lst_name):
        lst = getattr(self, lst_name, None)
        if lst is None:
            lst = []
            setattr(self, lst_name, lst)
        return lst

    def _cont_render(self, lst_name, lno, store, pfx=''):
        lines = []
        for item in self._list(lst_name):
            lines.extend(item.render(lno + len(lines), store, pfx))
        return lines

    def _len(self, lst_name, fld, cache, reducer, type_=None):
        max_len = getattr(self, cache, None)
        if max_len is None:
            max_len = max(
                len(six.text_type(getattr(o, fld)))
                for o in self._list(lst_name)
                if type_ is None or isinstance(o, type_)
            )
            setattr(self, cache, max_len)

        return max_len - len(reducer or '')

    def _append(self, lst_name, item, resetter=None):
        assert item is not None
        self._list(lst_name).append(item)
        if resetter:
            resetter()


class Option(Statement):
    @classmethod
    def match(cls, parser, lno, line, comment):
        if parser.tok(line) == 'option':
            name, value = parser.split_eq(
                parser.strip_semi(
                    line[len('option'):], lno,
                )
            )
            return cls(
                parser.fname, lno, parser.stack,
                name, value,
                comment=comment,
            )

        return None

    def __init__(self, fname, lno, container, name, value, comment=None):
        super(Option, self).__init__(fname, lno)

        self.container = container
        self.name = name
        self.value = value
        self.comment = comment

    def render(self, lno, store, pfx=''):
        line = '%soption %-*s = %s;' % (
            pfx, self.container.opt_name_len(), self.name, self.value,
        )

        if self.comment:
            line += '%*s // %s' % (
                self.container.opt_value_len(self.value), '', self.comment,
            )

        return [line]


class InlineOption(Option):
    def render(self, lno, store, pfx=''):
        return ['%s=%s' % (self.name, self.value)]


class OptionContainer(Container):
    def _reset_options(self):
        self._opt_name_len = None
        self._opt_value_len = None

    def opt_add(self, opt):
        self._append('options', opt, self._reset_options)

    def opt_render(self, lno, store, pfx=''):
        return self._cont_render('options', lno, store, pfx)

    def opt_name_len(self, reducer=''):
        return self._len('options', 'name', '_opt_name_len', reducer, Option)

    def opt_value_len(self, reducer=''):
        return self._len('options', 'value', '_opt_value_len', reducer, Option)


class InlineOptionContainer(OptionContainer):
    def opt_render(self, lno, store, pfx=''):
        opts = self._cont_render('options', lno, store, pfx)
        if opts:
            return [' [%s]' % ','.join(opts)]
        return []

    def opt_parse(self, parser, lno, line):
        if line[0] != '[' or line[-1] != ']':
            raise PBException(
                'Invalid inline option "%s"' % line,
                fname=parser.fname,
                lno=lno,
            )
        line = line[1:-1]

        name = None
        start = 0
        escape = False
        quoted = False
        for i in range(len(line)):
            if start is None:
                start = i

            if escape:
                escape = False
                continue

            if quoted:
                if line[i] == '\\':
                    escape = True
                if line[i] == '"':
                    quoted = False
                continue

            if name is None and line[i] == '=':
                name = line[start:i].strip()
                if not name:
                    raise PBException(
                        'Invalid option with empty name',
                        fname=parser.fname,
                        lno=lno,
                    )
                start = None
            elif name is not None:
                if line[i] == '"':
                    quoted = True
                elif line[i] == ',':
                    value = line[start:i].strip()
                    if not value:
                        raise PBException(
                            'Invalid option with empty value',
                            fname=parser.fname,
                            lno=lno,
                        )
                    self.opt_add(InlineOption(
                        parser.fname, lno, self,
                        name, line[start:i + 1],
                    ))
                    name = None
                    start = None

        if name is None or start is None:
            raise PBException(
                'Invalid inline option',
                fname=parser.fname,
                lno=lno,
            )

        self.opt_add(InlineOption(
            parser.fname, lno, self,
            name, line[start:],
        ))

    @property
    def opts(self):
        if getattr(self, '_opts', None) is None:
            opts = self.opt_render(0, None, '')
            self._opts = opts[0] if opts else ''
        return self._opts


class Field(Statement, InlineOptionContainer):
    @classmethod
    def match(cls, parser, lno, line, comment, labeled=False):
        desc, remainder = parser.split_eq(parser.strip_semi(line, lno))

        # Extract field number from remainder
        flen, field = parser.extract_digits(remainder, lno)
        remainder = remainder[flen:].strip()

        label = parser.tok(line)
        label_set = {'repeated'}
        if labeled:
            label_set |= {'optional', 'required'}
        if label in label_set:
            desc = desc[len(label):].strip()
        else:
            label = ''

        try:
            type_, name = desc.split()
        except ValueError:
            raise PBException(
                'Invalid field description "%s"' % desc,
                fname=parser.fname,
                lno=lno,
            )

        fld = cls(
            parser.fname, lno, parser.stack,
            type_, name, field,
            comment=comment,
            label=label,
        )

        # Add inline options
        if remainder:
            fld.opt_parse(parser, lno, remainder)

        return fld

    def __init__(self, fname, lno, container, type_, name, value,
                 comment=None, label=''):
        super(Field, self).__init__(fname, lno)

        self.container = container
        self.type_ = type_
        self.name = name
        self.value = value
        self.comment = comment
        self.label = label

    def render(self, lno, store, pfx=''):
        line = '%s%-*s %-*s = %*d%s;' % (
            pfx,
            self.container.fld_type_len(), self.full_type,
            self.container.fld_name_len(), self.name,
            self.container.fld_value_len(), self.value,
            self.opts,
        )

        if self.comment:
            line += '%*s // %s' % (
                self.container.fld_opts_len(self.opts), '',
                self.comment,
            )

        return [line]

    @property
    def full_type(self):
        if self.label:
            return '%s %s' % (self.label, self.type_)
        return self.type_


class MapField(Field):
    @classmethod
    def match(cls, parser, lno, line, comment):
        if parser.tok(line) == 'map':
            desc, remainder = parser.split_eq(parser.strip_semi(
                line[len('map'):], lno,
            ))

            # Extract field number from remainder
            flen, field = parser.extract_digits(remainder, lno)
            remainder = remainder[flen:].strip()

            # Make sure it's valid syntax
            type_end = desc.index('>')
            if (not desc or desc[0] != '<' or type_end < 0 or
                    desc.count(',') != 1):
                raise PBException(
                    'Invalid map field description "%s"' % desc,
                    fname=parser.fname,
                    lno=lno,
                )

            key_type, value_type = [
                p.strip() for p in desc[1:type_end].split(',')
            ]
            name = desc[type_end + 1:].strip()

            fld = cls(
                parser.fname, lno, parser.stack,
                key_type, value_type, name, field,
                comment=comment,
            )

            # Add inline options
            if remainder:
                fld.opt_parse(parser, lno, remainder)

            return fld

        return None

    def __init__(self, fname, lno, container, key_type, value_type, name,
                 value, comment=None):
        super(MapField, self).__init__(
            fname, lno, container,
            key_type, name, value,
            comment=comment,
        )

        self.value_type = value_type

    @property
    def full_type(self):
        return 'map<%s, %s>' % (self.type_, self.value_type)


class FieldContainer(Container):
    def _reset_fields(self):
        self._fld_type_len = None
        self._fld_name_len = None
        self._fld_value_len = None
        self._fld_opts_len = None

    def fld_add(self, fld):
        self._append('fields', fld, self._reset_fields)

    def fld_render(self, lno, store, pfx=''):
        return self._cont_render('fields', lno, store, pfx)

    def fld_type_len(self, reducer=''):
        return self._len(
            'fields', 'full_type', '_fld_type_len', reducer, Field,
        )

    def fld_name_len(self, reducer=''):
        return self._len('fields', 'name', '_fld_name_len', reducer, Field)

    def fld_value_len(self, reducer=''):
        return self._len('fields', 'value', '_fld_value_len', reducer, Field)

    def fld_opts_len(self, reducer=''):
        return self._len('fields', 'opts', '_fld_opts_len', reducer, Field)


class Enum(Statement, InlineOptionContainer):
    @classmethod
    def match(cls, parser, lno, line, comment):
        name, remainder = parser.split_eq(parser.strip_semi(line, lno))

        # Extract value from remainder
        vlen, value = parser.extract_digits(remainder, lno)
        remainder = remainder[vlen:].strip()

        enum = cls(
            parser.fname, lno, parser.stack,
            name, value,
            comment=comment,
        )

        # Add inline options
        if remainder:
            enum.opt_parse(parser, lno, remainder)

        return enum

    def __init__(self, fname, lno, container, name, value, comment=None):
        super(Enum, self).__init__(fname, lno)

        self.container = container
        self.name = name
        self.value = value
        self.comment = comment

    def render(self, lno, store, pfx=''):
        line = '%s%-*s = %*d%s;' % (
            pfx,
            self.container.enum_name_len(), self.name,
            self.container.enum_value_len(), self.value,
            self.opts,
        )

        if self.comment:
            line += '%*s // %s' % (
                self.container.enum_opts_len(self.opts), '',
                self.comment,
            )

        return [line]


class EnumContainer(Container):
    def _reset_enum(self):
        self._enum_name_len = None
        self._enum_value_len = None
        self._enum_opts_len = None

    def enum_add(self, enum):
        self._append('enum', enum, self._reset_enum)

    def enum_render(self, lno, store, pfx=''):
        return self._cont_render('enum', lno, store, pfx)

    def enum_name_len(self, reducer=''):
        return self._len('enum', 'name', '_enum_name_len', reducer, Enum)

    def enum_value_len(self, reducer=''):
        return self._len('enum', 'value', '_enum_value_len', reducer, Enum)

    def enum_opts_len(self, reducer=''):
        return self._len('enum', 'opts', '_enum_opts_len', reducer, Enum)


class Range(object):
    def __init__(self, low, high=None):
        self.low = low
        self.high = high

    def render(self):
        if self.high is None:
            return '%d to max'
        return '%d to %d'


class Reserved(Statement):
    @classmethod
    def match(cls, parser, lno, line, comment):
        if parser.tok(line) == 'reserved':
            ranges_txt = parser.strip_semi(line[len('reserved'):], lno)
            ranges = []
            if ranges_txt and ranges_txt[0] == '"':
                while ranges_txt:
                    ranges.append(parser.extract_strlit(ranges_txt, lno))
                    ranges_txt = ranges_txt[len(tmp):].strip()
                    if ranges_txt and ranges_txt[0] == ',':
                        ranges_txt = ranges_txt[1:].strip()
                        if not ranges_txt:
                            raise PBException(
                                'Too many commas',
                                fname=parser.fname,
                                lno=lno,
                            )
            else:
                parts = [p.strip() for p in ranges_txt.split(',')]
                for part in parts:
                    if part.isdigit():
                        ranges.append(int(part))
                    elif not part:
                        raise PBException(
                            'Too many commas',
                            fname=parser.fname,
                            lno=lno,
                        )
                    else:
                        ilen, low = parser.extract_digits(part, lno)
                        high_txt = part[ilen:]
                        if parser.tok(high_txt) != 'to':
                            raise PBException(
                                'Invalid reserved range "%s"' % part,
                                fname=parser.fname,
                                lno=lno,
                            )
                        high_txt = high_text[len('to'):].strip()
                        if parser.tok(high_text) == 'max':
                            high = None
                        else:
                            try:
                                high = int(high_txt)
                            except ValueError:
                                raise PBException(
                                    'Invalid reserved range "%s"' % part,
                                    fname=parser.fname,
                                    lno=lno,
                                )
                        ranges.append(Range(low, high))
            return cls(
                parser.fname, lno, parser.stack,
                ranges,
                comment=comment,
            )

        return None

    def __init__(self, fname, lno, container, ranges, comment=None):
        super(Reserved, self).__init__(fname, lno)

        self.container = container
        self.ranges = ranges
        self.comment = comment

        self._content = None

    def render(self, lno, store, pfx=''):
        line = '%sreserved %s;' % (pfx, self.content)

        if self.comment:
            line += '%*s // %s' % (
                self.container.resv_len(self.content), '', self.comment,
            )

        return [line]

    @property
    def content(self):
        if self._content is None:
            ranges = [
                rng if isinstance(rng, six.string_types) else
                ('%d' % rng if isinstance(rng, six.integer_types) else
                 rng.render())
                for rng in self.ranges
            ]
            self._content = ', '.join(ranges)


class ReservedContainer(Container):
    def _reset_reserved(self):
        self._resv_len = None

    def resv_add(self, resv):
        self._append('reserved', resv, self._reset_reserved)

    def resv_render(self, lno, store, pfx=''):
        return self._cont_render('reserved', lno, store, pfx)

    def resv_len(self, reducer=''):
        return self._len('reserved', 'content', '_resv_len', reducer, Reserved)


class Import(Statement):
    @classmethod
    def match(cls, parser, lno, line, comment):
        if parser.tok(line) == 'import':
            line = parser.strip_semi(line[len('import'):], lno)
            type_ = None
            if line[0] != '"':
                type_ = parser.tok(line)
                line = line[len(type_):].strip()

            return cls(
                parser.fname, lno, parser.stack,
                parser.extract_strlit(line, lno),
                comment=comment,
                type_=type_,
            )

        return None

    def __init__(self, fname, lno, container, iname, comment=None, type_=None):
        super(Import, self).__init__(fname, lno)

        self.container = container
        self.iname = iname
        self.comment = comment
        self.type_ = type_

        self._content = None

    def render(self, lno, store, pfx=''):
        line = '%simport %s;' % (pfx, self.content)

        if self.comment:
            line += '%*s // %s' % (
                self.container.import_len(self.content), '', self.comment,
            )

        return [line]

    @property
    def content(self):
        if self._content is None:
            if self.type_ is None:
                self._content = self.iname
            else:
                self._content = '%s %s' % (self.type_, self.iname)
        return self._content


class ImportContainer(Container):
    def _reset_imports(self):
        self._import_len = None

    def import_add(self, imp):
        self._append('imports', imp, self._reset_imports)

    def import_render(self, lno, store, pfx=''):
        return self._cont_render('imports', lno, store, pfx)

    def import_len(self, reducer=''):
        return self._len('imports', 'content', '_import_len', reducer, Import)


class Syntax(Statement):
    @classmethod
    def match(cls, parser, lno, line, comment):
        if parser.tok(line) == 'syntax':
            _stmt, syntax = parser.split_eq(parser.strip_semi(line, lno))
            if not syntax or syntax[0] != '"' or syntax[-1] != '"':
                raise PBException(
                    'Invalid syntax statement',
                    fname=parser.fname,
                    lno=lno,
                )
            return cls(
                parser.fname, lno, parser.stack,
                syntax,
                comment=comment,
            )

        return None

    def __init__(self, fname, lno, container, syntax, comment=None):
        super(Syntax, self).__init__(fname, lno)

        self.container = container
        self.syntax = syntax
        self.comment = comment

    def render(self, lno, store, pfx=''):
        line = '%ssyntax = %s;' % (pfx, self.syntax)

        if self.comment:
            line += ' // %s' % self.comment

        return [line]


class Package(Statement):
    @classmethod
    def match(cls, parser, lno, line, comment):
        if parser.tok(line) == 'package':
            return cls(
                parser.fname, lno, parser.stack,
                parser.strip_semi(line[len('package'):], lno),
                comment=comment,
            )

        return None

    def __init__(self, fname, lno, container, name, comment=None):
        super(Package, self).__init__(fname, lno)

        self.container = container
        self.name = name
        self.comment = comment

    def render(self, lno, store, pfx=''):
        line = '%spackage %s;' % (pfx, self.name)

        if self.comment:
            line += ' // %s' % self.comment

        return [line]


class StatementContainer(Container):
    def stmt_add(self, stmt):
        self._append('statements', stmt)

    def stmt_render(self, lno, store, pfx=''):
        lines = []
        for stmt in self._list('statements'):
            if lines:
                lines.append('')
            lines.extend(stmt.render(lno + len(lines), store, pfx))
        return lines


class Block(Statement):
    INDENT = '    '

    def __init__(self, fname, lno, container, name, prefix=None, comment=None):
        super(Block, self).__init__(fname, lno)

        self.container = container
        self.prefix = prefix
        self.comment = comment
        self.name = name

        self.end_comment = None

    def _render_prefix(self, lno, store, pfx):
        # Render the lead-in comment
        lines = self.prefix.render(lno, store, pfx) if self.prefix else []

        # Render the block start
        text = '%s%s %s {' % (pfx, self.TYPE, self.name)
        if self.comment:
            text += ' // %s' % self.comment
        lines.append(text)

        return lines

    def _render_block(self, lno, store, pfx, lines, renderers):
        sep = False
        for renderer in renderers:
            tmp = renderer(lno + len(lines), store, pfx + self.INDENT)
            if tmp:
                if sep:
                    lines.append('')
                lines.extend(tmp)
                sep = True

    def _render_suffix(self, lno, store, pfx, lines):
        text = '%s}' % pfx
        if self.end_comment:
            text += ' // %s' % self.end_comment
        lines.append(text)

        return lines

    def _render(self, lno, store, pfx, *renderers):
        # Render the lead-in
        lines = self._render_prefix(lno, store, pfx)

        # Render the block
        self._render_block(lno, store, pfx, lines, renderers)

        # Render the lead-out and return the lines
        return self._render_suffix(lno, store, pfx, lines)

    def set_end_comment(self, comment):
        self.end_comment = comment

    @abc.abstractmethod
    def parse(self, parser, lno, line, comment):
        pass

    @abc.abstractproperty
    def TYPE(self):
        pass


class NamedBlock(Block):
    def __init__(self, fname, lno, container, name, prefix=None, comment=None):
        super(NamedBlock, self).__init__(
            fname, lno, container, name, prefix, comment,
        )

        self._full_name = None

    def _data(self, lno, store, error=True):
        key = '%s:%s' % (self.TYPE, self.full_name)
        if error and key in store:
            raise PBException(
                'Duplicate %s %s' % (self.TYPE, self.full_name),
                fname=self.fname,
                lno=self.lno,
            )
        return store.setdefault(key, {'start': lno + 1})

    def _render_prefix(self, lno, store, pfx):
        # Get the data; also sets the absolute start
        data = self._data(lno, store)

        # Render the prefix
        lines = super(NamedBlock, self)._render_prefix(lno, store, pfx)

        # Store the line number of the block start
        data['block_start'] = lno + len(lines)

        return lines

    def _render_suffix(self, lno, store, pfx, lines):
        # Render the suffix
        super(NamedBlock, self)._render_suffix(lno, store, pfx, lines)

        # Save the data end
        self._data(lno, store, False)['end'] = lno + len(lines) + 1

        return lines

    @property
    def full_name(self):
        if self._full_name is None:
            if self.container and hasattr(self.container, 'full_name'):
                self._full_name = '%s.%s' % (
                    self.container.full_name, self.name,
                )
            else:
                self._full_name = self.name

        return self._full_name


class BlockContainer(Container):
    def block_add(self, block):
        self._append('blocks', block)

    def block_render(self, lno, store, pfx=''):
        lines = []
        for block in self._list('blocks'):
            if lines:
                lines.append('')
            lines.extend(block.render(lno + len(lines), store, pfx))
        return lines


class BlockComment(Block):
    TYPE = '<comment>'

    @classmethod
    def match(cls, parser, lno, line, comment):
        if not line and comment:
            return cls(
                parser.fname, lno, parser.stack,
                comment=comment,
            )

        return None

    def __init__(self, fname, lno, container, comment):
        super(BlockComment, self).__init__(fname, lno, container, None)

        self.text = [comment]

    def add_text(self, text):
        self.text.append(text)

    def render(self, lno, store, pfx=''):
        return [
            '%s// %s' % (pfx, text)
            for text in self.text
        ]

    def parse(self, parser, lno, line, comment):
        if line:
            parser.pop()
            return True

        self.add_text(comment)
        return False


class MessageBlock(NamedBlock, OptionContainer, FieldContainer,
                   ReservedContainer):
    TYPE = 'message'

    @classmethod
    def match(cls, parser, lno, line, comment, leadin=None):
        if parser.tok(line) == 'message':
            name = parser.strip_brace(line[len('message'):], lno)
            return cls(
                parser.fname, lno, parser.stack,
                name,
                prefix=leadin,
                comment=comment,
            )

        return None

    def render(self, lno, store, pfx=''):
        return self._render(
            lno, store, pfx,
            self.opt_render, self.resv_render, self.fld_render,
        )

    def parse(self, parser, lno, line, comment):
        if line == '}':
            if parser.data.block_comment:
                self.fld_add(parser.data.block_comment)
            if comment:
                self.set_end_comment(comment)
            parser.pop()
            return False

        cmnt = BlockComment.match(parser, lno, line, comment)
        if cmnt is not None:
            parser.data.block_comment = cmnt
            parser.push(cmnt)
            return False

        opt = Option.match(parser, lno, line, comment)
        if opt is not None:
            if parser.data.block_comment:
                self.opt_add(parser.data.block_comment)
                del parser.data.block_comment
            self.opt_add(opt)
            return False

        resv = Reserved.match(parser, lno, line, comment)
        if resv is not None:
            if parser.data.block_comment:
                self.resv_add(parser.data.block_comment)
                del parser.data.block_comment
            self.resv_add(resv)
            return False

        msg = MessageBlock.match(
            parser, lno, line, comment, parser.data.block_comment,
        )
        if msg is not None:
            self.fld_add(msg)
            del parser.data.block_comment
            parser.push(msg)
            return False

        enum = EnumBlock.match(
            parser, lno, line, comment, parser.data.block_comment,
        )
        if enum is not None:
            self.fld_add(enum)
            del parser.data.block_comment
            parser.push(enum)
            return False

        oneof = OneofBlock.match(
            parser, lno, line, comment, parser.data.block_comment,
        )
        if oneof is not None:
            self.fld_add(oneof)
            del parser.data.block_comment
            parser.push(oneof)
            return False

        map_ = MapField.match(
            parser, lno, line, comment,
        )
        if map_ is not None:
            if parser.data.block_comment:
                self.fld_add(parser.data.block_comment)
                del parser.data.block_comment
            self.fld_add(map_)
            return False

        if parser.data.block_comment:
            self.fld_add(parser.data.block_comment)
            del parser.data.block_comment

        if line:
            self.fld_add(Field.match(parser, lno, line, comment))

        return False


class EnumBlock(NamedBlock, OptionContainer, EnumContainer, ReservedContainer):
    TYPE = 'enum'

    @classmethod
    def match(cls, parser, lno, line, comment, leadin=None):
        if parser.tok(line) == 'enum':
            name = parser.strip_brace(line[len('enum'):], lno)
            return cls(
                parser.fname, lno, parser.stack,
                name,
                prefix=leadin,
                comment=comment,
            )

        return None

    def render(self, lno, store, pfx=''):
        return self._render(
            lno, store, pfx,
            self.opt_render, self.resv_render, self.enum_render,
        )

    def parse(self, parser, lno, line, comment):
        if line == '}':
            if parser.data.block_comment:
                self.enum_add(parser.data.block_comment)
            if comment:
                self.set_end_comment(comment)
            parser.pop()
            return False

        cmnt = BlockComment.match(parser, lno, line, comment)
        if cmnt is not None:
            parser.data.block_comment = cmnt
            parser.push(cmnt)
            return False

        opt = Option.match(parser, lno, line, comment)
        if opt is not None:
            if parser.data.block_comment:
                self.opt_add(parser.data.block_comment)
                del parser.data.block_comment
            self.opt_add(opt)
            return False

        resv = Reserved.match(parser, lno, line, comment)
        if resv is not None:
            if parser.data.block_comment:
                self.resv_add(parser.data.block_comment)
                del parser.data.block_comment
            self.resv_add(resv)
            return False

        if parser.data.block_comment:
            self.enum_add(parser.data.block_comment)
            del parser.data.block_comment

        if line:
            self.enum_add(Enum.match(parser, lno, line, comment))

        return False


class OneofBlock(Block, FieldContainer):
    TYPE = 'oneof'

    @classmethod
    def match(cls, parser, lno, line, comment, leadin=None):
        if parser.tok(line) == 'oneof':
            name = parser.strip_brace(line[len('oneof'):], lno)
            return cls(
                parser.fname, lno, parser.stack,
                name,
                prefix=leadin,
                comment=comment,
            )

        return None

    def render(self, lno, store, pfx=''):
        return self._render(lno, store, pfx, self.fld_render)

    def parse(self, parser, lno, line, comment):
        if line == '}':
            if parser.data.block_comment:
                self.fld_add(parser.data.block_comment)
            if comment:
                self.set_end_comment(comment)
            parser.pop()
            return False

        cmnt = BlockComment.match(parser, lno, line, comment)
        if cmnt is not None:
            parser.data.block_comment = cmnt
            parser.push(cmnt)
            return False

        if parser.data.block_comment:
            self.fld_add(parser.data.block_comment)
            del parser.data.block_comment

        if line:
            self.fld_add(Field.match(parser, lno, line, comment))

        return False


class ExtendBlock(NamedBlock, FieldContainer):
    TYPE = 'extend'

    @classmethod
    def match(cls, parser, lno, line, comment, leadin=None):
        if parser.tok(line) == 'extend':
            name = parser.strip_brace(line[len('extend'):], lno)
            return cls(
                parser.fname, lno, parser.stack,
                name,
                prefix=leadin,
                comment=comment,
            )

        return None

    def render(self, lno, store, pfx=''):
        return self._render(
            lno, store, pfx,
            self.fld_render,
        )

    def parse(self, parser, lno, line, comment):
        if line == '}':
            if parser.data.block_comment:
                self.fld_add(parser.data.block_comment)
            if comment:
                self.set_end_comment(comment)
            parser.pop()
            return False

        cmnt = BlockComment.match(parser, lno, line, comment)
        if cmnt is not None:
            parser.data.block_comment = cmnt
            parser.push(cmnt)
            return False

        if parser.data.block_comment:
            self.fld_add(parser.data.block_comment)
            del parser.data.block_comment

        if line:
            self.fld_add(Field.match(parser, lno, line, comment, labeled=True))

        return False


class FileBlock(Block, StatementContainer, ImportContainer, OptionContainer,
                BlockContainer):
    TYPE = '<file>'
    INDENT = ''

    @classmethod
    def match(cls, parser, lno, line, comment):
        raise NotImplementedError('FileBlock.match() should not be called')

    def __init__(self, fname):
        super(FileBlock, self).__init__(fname, 0, None, None)

    def render(self, lno, store, pfx=''):
        lines = []

        self._render_block(
            lno, store, pfx, lines, [
                self.stmt_render,
                self.import_render,
                self.opt_render,
                self.block_render,
            ]
        )

        return lines

    def parse(self, parser, lno, line, comment):
        if line is None:
            if parser.data.block_comment:
                self.block_add(parser.data.block_comment)
            return False

        cmnt = BlockComment.match(parser, lno, line, comment)
        if cmnt is not None:
            parser.data.block_comment = cmnt
            parser.push(cmnt)
            return False

        syntax = Syntax.match(parser, lno, line, comment)
        if syntax is not None:
            if parser.data.block_comment:
                self.stmt_add(parser.data.block_comment)
                del parser.data.block_comment
            self.stmt_add(syntax)
            return False

        package = Package.match(parser, lno, line, comment)
        if package is not None:
            if parser.data.block_comment:
                self.stmt_add(parser.data.block_comment)
                del parser.data.block_comment
            self.stmt_add(package)
            return False

        import_ = Import.match(parser, lno, line, comment)
        if import_ is not None:
            if parser.data.block_comment:
                self.import_add(parser.data.block_comment)
                del parser.data.block_comment
            self.import_add(import_)
            return False

        opt = Option.match(parser, lno, line, comment)
        if opt is not None:
            if parser.data.block_comment:
                self.opt_add(parser.data.block_comment)
                del parser.data.block_comment
            self.opt_add(opt)
            return False

        msg = MessageBlock.match(
            parser, lno, line, comment, parser.data.block_comment,
        )
        if msg is not None:
            self.block_add(msg)
            del parser.data.block_comment
            parser.push(msg)
            return False

        extend = ExtendBlock.match(
            parser, lno, line, comment, parser.data.block_comment,
        )
        if extend is not None:
            self.block_add(extend)
            del parser.data.block_comment
            parser.push(extend)
            return False

        enum = EnumBlock.match(
            parser, lno, line, comment, parser.data.block_comment,
        )
        if enum is not None:
            self.block_add(enum)
            del parser.data.block_comment
            parser.push(enum)
            return False

        if parser.data.block_comment:
            self.block_add(parser.data.block_comment)
            del parser.data.block_comment

        return False


class ParserData(object):
    def __init__(self):
        self._data = {}

    def __getattr__(self, name):
        return self._data.get(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super(ParserData, self).__setattr__(name, value)
        else:
            self._data[name] = value

    def __delattr__(self, name):
        if name.startswith('_'):
            super(ParserData, self).__delattr__(name)
        else:
            self._data.pop(name, None)


class Protobuf(object):
    def __init__(self, pbfile):
        self.pbfile = pbfile
        self.locations = {}

    def render(self):
        return self.pbfile.render(1, self.locations)


class Parser(object):
    @classmethod
    def parse(cls, fname):
        parser = cls(fname)
        return Protobuf(parser.parse_file())

    def __init__(self, fname):
        self.fname = fname

        self._stack = []
        self._data = []

    def push(self, parser):
        assert parser is not None
        self._stack.append(parser)
        self._data.append(ParserData())

    def pop(self):
        self._data.pop()
        return self._stack.pop()

    def parse_file(self):
        self.push(FileBlock(self.fname))
        with open(self.fname) as f:
            for lno, line in enumerate(f, 1):
                # Expanding the tabs guarantees comments still look
                # the same
                line, comment = self.split_comment(line.expandtabs())
                while self.stack.parse(self, lno, line, comment):
                    pass

        if len(self._stack) > 1:
            raise PBException(
                'Unclosed %s block' % self.stack.TYPE,
                fname=self.fname,
                lno=self.stack.lno,
            )

        # Notify the file block of the last line
        self.stack.parse(self, lno, None, None)

        return self.pop()

    def tok(self, line):
        for i in range(len(line)):
            if not (line[i].isalnum() or line[i] == '_'):
                return line[:i]
        return line

    def split_comment(self, line):
        line, _sep, comment = line.partition('//')
        comment = comment.rstrip()
        if comment and comment[0].isspace():
            comment = comment[1:]
        return (line.strip(), comment or None)

    def split_eq(self, line):
        line, _sep, value = line.partition('=')
        return (line.strip(), value.strip())

    def strip_semi(self, line, lno):
        if line[-1] != ';':
            raise PBException(
                'Missing semicolon',
                fname=self.fname,
                lno=lno,
            )
        return line[:-1].strip()

    def strip_brace(self, line, lno):
        if line[-1] != '{':
            raise PBException(
                'Missing open brace',
                fname=self.fname,
                lno=lno,
            )
        return line[:-1].strip()

    def extract_strlit(self, line, lno):
        assert line[0] == '"'
        escape = False
        for i in range(1, len(line)):
            if escape:
                escape = False
                continue

            if line[i] == '\\':
                escape = True

            if line[i] == '"':
                return line[:i + 1]

        raise PBException(
            'Unclosed string literal',
            fname=self.fname,
            lno=lno,
        )

    def extract_digits(self, line, lno):
        if not line or not line[0].isdigit():
            raise PBException(
                'Invalid number',
                fname=self.fname,
                lno=lno,
            )

        for i in range(len(line)):
            if not line[i].isdigit():
                break
        else:
            return len(line), int(line)

        return i, int(line[:i])

    @property
    def stack(self):
        return self._stack[-1]

    @property
    def data(self):
        return self._data[-1]


@cli_tools.argument(
    'files',
    nargs='+',
    help='The protobuf files to reformat.',
)
@cli_tools.argument(
    '--debug', '-d',
    action='store_true',
    help='Enable debugging output.',
)
def main(files):
    for fname in files:
        print('Processing file %s' % fname)

        pbfile = Parser.parse(fname)

        shutil.move(fname, fname + '~')
        with open(fname, 'w') as f:
            print('\n'.join(pbfile.render()), file=f)

        idx = os.path.splitext(fname)[0] + '.idx'
        if os.path.exists(idx):
            shutil.move(idx, idx + '~')
        with open(idx, 'w') as f:
            yaml.safe_dump(
                pbfile.locations, f,
                default_flow_style=False,
                explicit_start=True,
            )


if __name__ == '__main__':
    sys.exit(main.console())
