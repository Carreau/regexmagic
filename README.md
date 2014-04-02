regexmagic
==========

A regular expression magic for the IPython Notebook that emulates some
of the capabilities of the interactive matcher at http://regexpal.com.

Usage:

    %%matchlines pattern
    text...
    text...
    text...

or:

    %matchfile filename pattern

Notes:

1.  IPython presently interprets {x} to mean 'expand variable x', so
    regular expressions like '\d{4}' must be written as '\d{{4}}' in
    order to get through IPython's parsing.  Fixing this will require
    changes to IPython itself; see
    [this thread](http://mail.scipy.org/pipermail/ipython-dev/2013-August/012259.html)
    in the IPython developers' mailing list.

2.  A pattern can have leading or trailing spaces, though for obvious
    reasons this is hard to read.  Output of patterns or text with
    leading or trailing spaces is incorrect, however, because spaces
    (and tabs) aren't converted to `&nbsp;` (non-breaking spaces):
    feeding `&nbsp;` into IPython's `HTML` function results in
    `&amp;nbsp;`, because `HTML` helpfully escapes the `&`.
