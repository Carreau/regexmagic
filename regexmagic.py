"""regexmagic provides a cell magic for the IPython Notebook called
%%regex that runs regular expressions against lines of text without
the clutter of re.search(...) calls.  The output is colorized to show
the span of each match.

Usage:

%%regex a+b
this text has no matches
this line has one match: aaab
about to match some more: aab

Note: IPython presently interprets {x} to mean 'expand variable x', so
      regular expressions like '\d{4}' must be written as '\d{{4}}'.
      We're working on it..."""

# This file is copyright 2013 by Matt Davis and Greg Wilson and
# covered by the license at
# https://github.com/gvwilson/regexmagic/blob/master/LICENSE

import re
from IPython.core.magic import Magics, magics_class, line_magic, cell_magic, line_cell_magic
from IPython.display import display, HTML
from IPython.html.widgets import interactive, fixed
from IPython.core.error import UsageError

PATTERN_TEMPL = '<span style="color:DarkGreen; font-weight:bold; font-style:italic;white-space: pre;">{0}</span><br/>'
ERROR_TEMPL = '<span style="color:Red; font-weight:bold; font-style:italic;white-space: pre;">{0}</span><br/>'
MATCH_TEMPL = '<span style="background:{0}; font-weight:bold;white-space: pre;">{1}</span>'
NOMATCH_TEMPL = '<span style="color:gray;white-space: pre;">{0}</span>'


@magics_class
class RegexMagic(Magics):
    '''Provide the 'regex' calling point for the magic, and keep track of
    alternating colors while matching.'''

    Colors = ['Pink', 'Yellow']

    @line_magic
    def matchfile(self, line, cell=None):
        '''Read in a file, and match the regular expression to it.'''
        pattern, text = self.handle_file(line)
        return self.matchlines(pattern, text)

    @cell_magic
    def imatchlines(self, pattern, text):
        return interactive(self.handle_text, pattern=pattern, text=fixed(text))

    @cell_magic
    def matchlines(self, pattern, text):
        return self.handle_text(pattern=pattern, text=text)

    def handle_file(self, line):
        parts = [x.strip() for x in line.split(' ', 1)]
        if len(parts) != 1:
            raise UsageError(
                "file matching magic should take one argument, "
                "the name of the file (you provided %d arguments)"
                % (len(parts) - 1))

        filename, pattern = parts
        with open(filename, 'r') as reader:
            text = reader.read()
        return pattern, text

    def handle_text(self, pattern='', text='', ignore_case=False, multiline=False, dot_all=False):
        # compile the regular expression, with flags
        flags = 0
        if ignore_case:
            flags = flags | re.IGNORECASE
        if multiline:
            flags = flags | re.MULTILINE
        if dot_all:
            flags = flags | re.DOTALL
        try:
            compiled_pattern = re.compile(pattern, flags)

        # handle the case where the regular expression is invalid
        except:
            msg = "Invalid regex: %s" % pattern
            html_disp = HTML(ERROR_TEMPL.format(msg))

        # handle the case where the regular expression is ok
        else:
            # this keeps track of the colors for alternating matches
            self.this_color, self.next_color = RegexMagic.Colors
            result_str = self.match(compiled_pattern, text).split('\n')
            pattern_str = PATTERN_TEMPL.format(pattern)
            html_disp = HTML(pattern_str + '<br/>'.join(result_str))

        display(html_disp)
        return html_disp

    def match(self, compiled_pattern, line):
        result = []
        m = compiled_pattern.search(line)
        n = 0
        while m:
            start = m.start()
            end = m.end()

            # format all text up to the current match
            result.append(NOMATCH_TEMPL.format(line[:start]))
            # format the current match
            result.append(MATCH_TEMPL.format(self.this_color, line[start:end]))

            # search for the next match
            line = line[end:]
            self.this_color, self.next_color = self.next_color, self.this_color
            m = compiled_pattern.search(line)

            n = n + 1
            if n > 100:
                break
                print 'more than 100 matches ?'

        if len(line) > 0:
            result.append(NOMATCH_TEMPL.format(line))

        return ''.join(result)

def load_ipython_extension(ipython):
    ipython.register_magics(RegexMagic)
