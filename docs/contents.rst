.. $Id$

=============================================
 Python Bindings for Berkeley DB 4.3 thru 5.3
=============================================

Introduction
------------

.. _Berkeley DB: http://www.oracle.com/technetwork/database/berkeleydb/overview/index.html

This handcrafted package contains Python wrappers for `Berkeley DB`_,
the Open Source embedded database system. Berkeley DB is a programmatic
toolkit that provides high-performance built-in database support for
desktop and server applications.

The Berkeley DB access methods include B+tree, Extended Linear Hashing,
Fixed and Variable-length records, and Queues. Berkeley DB provides full
transactional support, database recovery, online backups, multi-threaded
and multi-process access, etc.

The Python wrappers allow you to store Python string objects of any
length, keyed either by strings or integers depending on the database
access method. With the use of another module in the package standard
shelve-like functionality is provided allowing you to store any
picklable Python object! 

Berkeley DB is very powerful and versatile, but it is complex to
use correctly. :Oracle:`Oracle documentation <toc.htm>` is very
complete. Please, review it.

Documentation Index
-------------------

.. toctree::

  introduction.rst
  dbenv.rst
  db.rst
  dbcursor.rst
  dblogcursor.rst
  dbtxn.rst
  dblock.rst
  dbsequence.rst
  dbsite.rst
  history.rst

