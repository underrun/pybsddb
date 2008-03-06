
This directory contains the relevant bits from all previous versions
of the bsddb extension module.  Not all of each package is included,
just the main sources.  Because there has been many fingers messing
with this over time, and a few very different implementation
strategies, I felt that it is important to keep track of the old
sources to use for comparrison during development.  Each subdirectory
has a different version.


        1.85    The original extension module for Berkeley DB 1.85, as
                shipped with Python 2.0

        rpd     Robin Dunn's last release (1.2.0) of the extension and
                companion modules for Berkeley DB 2.7.x.  This version
                uses SWIG to generate the C wrapper code and the
                shadow-classes used in Python.

        gps     Gregory Smith's version 2.2.3 for Berkeley DB 3.1.x,
                derived from Robin's package.  This version also uses
                SWIG.

        amk     Andrew Kuchling's initial stab at producing a non-SWIG
                version of the extension module for Berkeley DB
                3.1.x.

  -- Robin