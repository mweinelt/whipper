# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import re
import os
import sys

# twisted's unittests have skip support, standard unittest don't
from twisted.trial import unittest

from morituri.configure import configure

# lifted from flumotion


def _diff(old, new, desc):
    import difflib
    lines = difflib.unified_diff(old, new)
    lines = list(lines)
    if not lines:
        return
    output = ''
    for line in lines:
        output += '%s: %s\n' % (desc, line[:-1])

    raise AssertionError(
        ("\nError while comparing strings:\n"
         "%s") % (output.encode('utf-8'), ))


def diffStrings(orig, new, desc='input'):

    assert type(orig) == type(new), 'type %s and %s are different' % (
        type(orig), type(new))

    def _tolines(s):
        return [line + '\n' for line in s.split('\n')]

    return _diff(_tolines(orig),
                 _tolines(new),
                 desc=desc)


class TestCase(unittest.TestCase):
    # unittest.TestCase.failUnlessRaises does not return the exception,
    # and we'd like to check for the actual exception under TaskException,
    # so override the way twisted.trial.unittest does, without failure

    def failUnlessRaises(self, exception, f, *args, **kwargs):
        try:
            result = f(*args, **kwargs)
        except exception, inst:
            return inst
        except exception, e:
            raise Exception('%s raised instead of %s:\n %s' %
                    (sys.exec_info()[0], exception.__name__, str(e))
            )
        else:
            raise Exception('%s not raised (%r returned)' %
                    (exception.__name__, result)
            )

    assertRaises = failUnlessRaises

    def readCue(self, name):
        """
        Read a .cue file, and replace the version comment with the current
        version so we can use it in comparisons.
        """
        ret = open(os.path.join(os.path.dirname(__file__), name)).read(
            ).decode('utf-8')
        ret = re.sub(
            'REM COMMENT "Morituri.*',
            'REM COMMENT "Morituri %s"' % (configure.version),
            ret, re.MULTILINE)

        return ret

class UnicodeTestMixin:
    # A helper mixin to skip tests if we're not in a UTF-8 locale

    try:
        os.stat(u'morituri.test.B\xeate Noire.empty')
    except UnicodeEncodeError:
        skip = 'No UTF-8 locale'
    except OSError:
        pass
