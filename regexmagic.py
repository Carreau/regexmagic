"""regexmagic provides several line and cell magics for the IPython
Notebook, which run regular expressions against lines of text without
the clutter of re.search(...) calls.  The output is colorized to show
the span of each match.

Available cell magics:
    matchlines
    imatchlines

Available line magics:
    matchfile
    imatchfile

Example usage:

%%matchlines a+b
this text has no matches
this line has one match: aaab
about to match some more: aab

Note: IPython presently interprets {x} to mean 'expand variable x', so
      regular expressions like '\d{4}' must be written as '\d{{4}}'.
      We're working on it...

"""

# This file is copyright 2013 by Matt Davis and Greg Wilson and
# covered by the license at
# https://github.com/gvwilson/regexmagic/blob/master/LICENSE

import re
from IPython.core.magic import Magics, magics_class, line_magic, cell_magic
from IPython.display import display, HTML
from IPython.html.widgets import interactive, fixed

# formatting templates
PATTERN_TEMPL = '<span style="color:DarkGreen; font-weight:bold; font-style:italic;white-space: pre;">{0}</span><br/>'
ERROR_TEMPL = '<span style="color:Red; font-weight:bold; font-style:italic;white-space: pre;">{0}</span><br/>'
MATCH_TEMPL = '<span style="background:{0}; font-weight:bold;white-space: pre;">{1}</span>'
NOMATCH_TEMPL = '<span style="color:gray;white-space: pre;">{0}</span>'


@magics_class
class RegexMagic(Magics):
    '''Provide the calling points for the magic, and keep track of
    alternating colors while matching.

    '''

    Colors = ['Pink', 'Yellow']

    @line_magic
    def imatchfile(self, line, cell=None):
        '''Perform regular expression matching on the given file, using an
        iteractively provided pattern.

        Usage: %imatchfile <filename>

        See the `%%imatchlines` cell magic for further documentation
        and a description of available options.

        '''
        filename = line.strip()
        with open(filename, 'r') as reader:
            text = reader.read()
        return self.imatchlines('', text)

    @line_magic
    def matchfile(self, line, cell=None):
        '''Perform regular expression matching on the given file using the
        given pattern.

        Usage: %matchfile <filename> <pattern>

        See the `%%matchlines` cell magic for further documentation.

        '''
        filename, pattern = line.split(' ', 1)
        filename = filename.strip()
        with open(filename, 'r') as reader:
            text = reader.read()
        return self.matchlines(pattern, text)

    @cell_magic
    def imatchlines(self, line, cell):
        '''Perform regular expression matching on the contents of the cell,
        using an interactively provided regular expression.

        Usage: %%imatchlines

        There are several options you can interactively specify:

        ignore_case: Perform case-insensitive matching;
        expressions like [A-Z] will match lowercase letters, too.

        multiline: When specified, the pattern character '^' matches
        at the beginning of the string and at the beginning of each
        line (immediately following each newline); and the pattern
        character '$' matches at the end of the string and at the end
        of each line (immediately preceding each newline). By default,
        '^' matches only at the beginning of the string, and '$' only
        at the end of the string and immediately before the newline
        (if any) at the end of the string.

        dotall: Make the '.' special character match any character at
        all, including a newline; without this flag, '.' will match
        anything except a newline.

        '''

        return interactive(self.display_regex, text=fixed(cell))

    @cell_magic
    def matchlines(self, line, cell):
        '''Perform regular expression matching on the cell contents using the
        given pattern.

        Usage: %matchlines <pattern>

        '''

        self.display_regex(pattern=line, text=cell)

    def display_regex(self, pattern='', text='',
                      ignore_case=False, multiline=False, dot_all=False):
        '''Compile the regular expression with the specified options, search
        for matches, and format them appropriately.

        '''
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

    def match(self, compiled_pattern, text):
        '''Search for regular expression matches using the given compiled
        pattern.

        '''
        result = []
        m = compiled_pattern.search(text)

        while m:
            start = m.start()
            end = m.end()
            # if the match is zero length, stop searching
            if start == end:
                break

            # format all text up to the current match
            result.append(NOMATCH_TEMPL.format(text[:start]))
            # format the current match
            result.append(MATCH_TEMPL.format(self.this_color, text[start:end]))

            # search for the next match
            text = text[end:]
            self.this_color, self.next_color = self.next_color, self.this_color
            m = compiled_pattern.search(text)

        if len(text) > 0:
            result.append(NOMATCH_TEMPL.format(text))

        return ''.join(result)


def load_ipython_extension(ipython):
    ipython.register_magics(RegexMagic)
