Ha Hong (hahong@mit; hahong84@gmail.com)
25 Jan 2011

This directory contains all the files needed to build the scarab IO
module (_data.so) for the Python package `mworks`.  As of now,
only Linux systems are supported.


1. How to Build and Install

% make
% make install


2. Some Notes

DataFileIndexer: this comes from `mw_datatools/DataFileIndexer` of the
`mw_datatools` package.  Some source files and Makefile are modified 
from the original branch (as of 25 Jan 2011).

Scarab: this comes from `mw_scarab/Scarab-0.1.00d19/c` of the `mw_scarab`
package.  The source files (*.c, *.h) are not changed from the main branch
(as of 25 Jan 2011), but the Makefile is different (e.g., -D__LITTLE_ENDIAN).

MWorksCore: assortment of header files from `mw_core` package.
