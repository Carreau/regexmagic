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

PATTERN_TEMPL = '<span style="color:DarkGreen; font-weight:bold; font-style:italic">{0}</span><br/>'
MATCH_TEMPL = '<span style="background:{0}; font-weight:bold">{1}</span>'
NOMATCH_TEMPL = '<span style="color:gray">{0}</span>'

@magics_class
class RegexMagic(Magics):
    '''Provide the 'regex' calling point for the magic, and keep track of
    alternating colors while matching.'''

    Colors = ['Pink', 'Yellow']

    @line_magic
    def matchfile(self, line, cell=None):
        filename, pattern = [x.strip() for x in line.split(' ', 1)]
        with open(filename, 'r') as reader:
            text = reader.read()
        self.matchlines(pattern, text)

    @cell_magic
    def matchlines(self, pattern, text):
        pattern_str = PATTERN_TEMPL.format(pattern)
        self.this_color, self.next_color = RegexMagic.Colors
        result_str = [self.handle_line(pattern, line) for line in text.split('\n')]
        display(HTML(pattern_str + '<br/>'.join(result_str)))

    def handle_line(self, pattern, line):
        result = []
        m = re.search(pattern, line)
        while m:
            result.append(NOMATCH_TEMPL.format(line[:m.start()]))
            result.append(MATCH_TEMPL.format(self.this_color, line[m.start():m.end()]))
            line = line[m.end():]
            self.this_color, self.next_color = self.next_color, self.this_color
            m = re.search(pattern, line)
        else:
            line = NOMATCH_TEMPL.format(line)
        result.append(line)
        return ''.join(result)

def load_ipython_extension(ipython):
    ipython.register_magics(RegexMagic)
