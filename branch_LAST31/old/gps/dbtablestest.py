#!/usr/bin/env python
#
#-----------------------------------------------------------------------
# A test suite for the table interface built on bsddb3.db
#-----------------------------------------------------------------------
#
# Copyright (C) 2000 by Autonomous Zone Industries
#
# March 20, 2000
#
# License:      This is free software.  You may use this software for any
#               purpose including modification/redistribution, so long as
#               this header remains intact and that you do not claim any
#               rights of ownership or authorship of this software.  This
#               software has been tested, but no warranty is expressed or
#               implied.
#
#   --  Gregory P. Smith <greg@electricrain.com>
#
# $Id$

# standard modules
import sys
try:
    import cPickle
    pickle = cPickle
except ImportError:
    import pickle
import re

# our modules
from bsddb3 import db, dbtables

# If our (Mojo Nation) unit testing module is available, use it
try:
    import RunTests
    test_db_home = RunTests.get_next_dir_name()
    mojo_test_flag = 0
    __use_RunTests = 1
except ImportError:
    __use_RunTests = 0
    # Directory that a test database environment will be opened in
    test_db_home = "tabletest"
test_db_name = "test-table.db3"


def test1() :
    mytable = dbtables.bsdTableDb(
        filename=test_db_name, dbhome=test_db_home, create=1)

    tabname = "Test1"
    colname = 'cool numbers'
    try:
        mytable.Drop(tabname)
    except dbtables.TableDbError:
        pass
    mytable.CreateTable(tabname, [colname])
    mytable.Insert(tabname, {colname: pickle.dumps(3.14159, 1)})

    #mytable._db_print()

    values = mytable.Select(tabname, [colname], conditions={colname: None})

    colval = pickle.loads(values[0][colname])
    assert(colval > 3.141 and colval < 3.142) 


def test2() :
    mytable = dbtables.bsdTableDb(
        filename=test_db_name, dbhome=test_db_home, create=1)

    tabname = "Birds!"
    col0 = 'coolness factor'
    col1 = 'but can it fly?'
    col2 = 'Species'
    testinfo = [
        {col0: pickle.dumps(8, 1), col1: 'no', col2: 'Penguin'},
        {col0: pickle.dumps(-1, 1), col1: 'no', col2: 'Turkey'},
        {col0: pickle.dumps(9, 1), col1: 'yes', col2: 'SR-71A Blackbird'}
    ]

    try:
        mytable.Drop(tabname)
    except dbtables.TableDbError:
        pass
    mytable.CreateTable(tabname, [col0, col1, col2])
    for row in testinfo :
        mytable.Insert(tabname, row)

    values = mytable.Select(tabname, [col2],
        conditions={col0: lambda x: pickle.loads(x) >= 8})

    assert len(values) == 2
    if values[0]['Species'] == 'Penguin' :
        assert values[1]['Species'] == 'SR-71A Blackbird'
    elif values[0]['Species'] == 'SR-71A Blackbird' :
        assert values[1]['Species'] == 'Penguin'
    else :
        print "values=", `values`
        raise "Wrong values returned!"

def test3() :
    mytable = dbtables.bsdTableDb(
        filename=test_db_name, dbhome=test_db_home, create=1)

    tabname = "Birds!"

    try:
        mytable.Drop(tabname)
    except dbtables.TableDbError:
        pass
    mytable.CreateTable(tabname, ['a', 'b', 'c', 'd', 'e'])
    mytable.Drop(tabname)
    mytable.CreateTable(tabname, ['a', 'b', 'c', 'd', 'e'])

    try:
        mytable.Insert(tabname, {'a': "", 'e': pickle.dumps([{4:5, 6:7}, 'foo'], 1), 'f': "Zero"})
        assert 0
    except dbtables.TableDbError:
        pass

    try:
        mytable.Select(tabname, [], conditions={'foo': '123'})
        assert 0
    except dbtables.TableDbError:
        pass

    mytable.Insert(tabname, {'a': '42', 'b': "bad", 'c': "meep", 'e': 'Fuzzy wuzzy was a bear'})
    mytable.Insert(tabname, {'a': '581750', 'b': "good", 'd': "bla", 'c': "black", 'e': 'fuzzy was here'})
    mytable.Insert(tabname, {'a': '800000', 'b': "good", 'd': "bla", 'c': "black", 'e': 'Fuzzy wuzzy is a bear'})

    #mytable._db_print()

    # this should return two rows
    values = mytable.Select(tabname, ['b', 'a', 'd'],
        conditions={'e': re.compile('wuzzy').search, 'a': re.compile('^[0-9]+$').match})
    assert len(values) == 2

    # now lets delete one of them and try again
    mytable.Delete(tabname, conditions={'b': dbtables.ExactCond('good')})
    values = mytable.Select(tabname, ['a', 'd', 'b'], conditions={'e': dbtables.PrefixCond('Fuzzy')})
    assert len(values) == 1
    assert values[0]['d'] == None

    values = mytable.Select(tabname, ['b'],
        conditions={'c': lambda c: c == 'meep'})
    assert len(values) == 1
    assert values[0]['b'] == "bad"
    

def test_CreateOrExtend():
    mytable = dbtables.bsdTableDb(
        filename=test_db_name, dbhome=test_db_home, create=1)

    tabname = "beer"

    mytable.CreateOrExtendTable(tabname, ['name', 'taste', 'filling', 'alcohol content', 'price'])
    try:
        mytable.Insert(tabname, {'taste': 'crap', 'filling': 'no', 'is it Guinness?': 'no'})
        assert 0, "Insert should've failed due to bad column name"
    except:
        pass
    mytable.CreateOrExtendTable(tabname, ['name', 'taste', 'is it Guinness?'])

    # these should both succeed as the table should contain the union of both sets of columns.
    mytable.Insert(tabname, {'taste': 'crap', 'filling': 'no', 'is it Guinness?': 'no'})
    mytable.Insert(tabname, {'taste': 'great', 'filling': 'yes', 'is it Guinness?': 'yes', 'name': 'Guinness'})


def test_CondObjs() :
    mytable = dbtables.bsdTableDb(
        filename=test_db_name, dbhome=test_db_home, create=1)

    tabname = "letters"

    mytable.CreateTable(tabname, ['a', 'b', 'c', 'd', 'e', 'p'])

    mytable.Insert(tabname, {'a': "the letter A", 'b': "the letter B", 'c': "is for cookie"})
    mytable.Insert(tabname, {'a': "is for aardvark", 'e': "the letter E", 'c': "is for cookie", 'd': "is for dog"})
    mytable.Insert(tabname, {'a': "the letter A", 'e': "the letter E", 'c': "is for cookie", 'p': "is for Python"})

    values = mytable.Select(tabname, ['p', 'e'], conditions={'e': dbtables.PrefixCond('the l')})
    assert len(values) == 2, values
    assert values[0]['e'] == values[1]['e'], values
    assert values[0]['p'] != values[1]['p'], values

    values = mytable.Select(tabname, ['d', 'a'], conditions={'a': dbtables.LikeCond('%aardvark%')})
    assert len(values) == 1, values
    assert values[0]['d'] == "is for dog", values
    assert values[0]['a'] == "is for aardvark", values

    values = mytable.Select(tabname, None, {'b': dbtables.Cond(), 'e':dbtables.LikeCond('%letter%'), 'a':dbtables.PrefixCond('is'), 'd':dbtables.ExactCond('is for dog'), 'c':dbtables.PrefixCond('is for'), 'p':lambda s: not s})
    assert len(values) == 1, values
    assert values[0]['d'] == "is for dog", values
    assert values[0]['a'] == "is for aardvark", values



def run():
    print "Testing bsddb3.dbtable..."
    test1()
    test1()
    test1()
    test1()
    test1()
    test2()
    test2()
    test2()
    test2()
    test2()
    test3()
    test3()
    test3()
    test3()
    test3()
    print "Tests passed"

if __name__ == '__main__' :
    if __use_RunTests :
        RunTests.runTests(["bsddb3.dbtablestest"])
    else :
        run()
