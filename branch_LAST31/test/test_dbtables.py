#!/usr/bin/env python
#
#-----------------------------------------------------------------------
# A test suite for the table interface built on bsddb3.db
#-----------------------------------------------------------------------
#
# Copyright (C) 2000, 2001 by Autonomous Zone Industries
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

import sys, os, re
try:
    import cPickle
    pickle = cPickle
except ImportError:
    import pickle

import unittest
from test_all import verbose

from bsddb3 import db, dbtables



#----------------------------------------------------------------------

class TableDBTestCase(unittest.TestCase):
    db_home = 'db_home'
    db_name = 'test-table.db'

    def setUp(self):
        homeDir = os.path.join(os.path.dirname(sys.argv[0]), 'db_home')
        self.homeDir = homeDir
        try: os.mkdir(homeDir)
        except os.error: pass
        self.tdb = dbtables.bsdTableDB(filename='tabletest.db', dbhome='db_home', create=1)

    def tearDown(self):
        self.tdb.close()
        import glob
        files = glob.glob(os.path.join(self.homeDir, '*'))
        for file in files:
            os.remove(file)

    def test01(self):
        tabname = "test01"
        colname = 'cool numbers'
        try:
            self.tdb.Drop(tabname)
        except dbtables.TableDBError:
            pass
        self.tdb.CreateTable(tabname, [colname])
        self.tdb.Insert(tabname, {colname: pickle.dumps(3.14159, 1)})

        if verbose:
            self.tdb._db_print()

        values = self.tdb.Select(tabname, [colname], conditions={colname: None})

        colval = pickle.loads(values[0][colname])
        assert(colval > 3.141 and colval < 3.142) 


    def test02(self):
        tabname = "test02"
        col0 = 'coolness factor'
        col1 = 'but can it fly?'
        col2 = 'Species'
        testinfo = [
            {col0: pickle.dumps(8, 1), col1: 'no', col2: 'Penguin'},
            {col0: pickle.dumps(-1, 1), col1: 'no', col2: 'Turkey'},
            {col0: pickle.dumps(9, 1), col1: 'yes', col2: 'SR-71A Blackbird'}
        ]

        try:
            self.tdb.Drop(tabname)
        except dbtables.TableDBError:
            pass
        self.tdb.CreateTable(tabname, [col0, col1, col2])
        for row in testinfo :
            self.tdb.Insert(tabname, row)

        values = self.tdb.Select(tabname, [col2],
            conditions={col0: lambda x: pickle.loads(x) >= 8})

        assert len(values) == 2
        if values[0]['Species'] == 'Penguin' :
            assert values[1]['Species'] == 'SR-71A Blackbird'
        elif values[0]['Species'] == 'SR-71A Blackbird' :
            assert values[1]['Species'] == 'Penguin'
        else :
            if verbose:
                print "values=", `values`
            raise "Wrong values returned!"

    def test03(self):
        tabname = "test03"
        try:
            self.tdb.Drop(tabname)
        except dbtables.TableDBError:
            pass
        if verbose:
            print '...before CreateTable...'
            self.tdb._db_print()
        self.tdb.CreateTable(tabname, ['a', 'b', 'c', 'd', 'e'])
        if verbose:
            print '...after CreateTable...'
            self.tdb._db_print()
        self.tdb.Drop(tabname)
        if verbose:
            print '...after Drop...'
            self.tdb._db_print()
        self.tdb.CreateTable(tabname, ['a', 'b', 'c', 'd', 'e'])

        try:
            self.tdb.Insert(tabname, {'a': "", 'e': pickle.dumps([{4:5, 6:7}, 'foo'], 1), 'f': "Zero"})
            assert 0
        except dbtables.TableDBError:
            pass

        try:
            self.tdb.Select(tabname, [], conditions={'foo': '123'})
            assert 0
        except dbtables.TableDBError:
            pass

        self.tdb.Insert(tabname, {'a': '42', 'b': "bad", 'c': "meep", 'e': 'Fuzzy wuzzy was a bear'})
        self.tdb.Insert(tabname, {'a': '581750', 'b': "good", 'd': "bla", 'c': "black", 'e': 'fuzzy was here'})
        self.tdb.Insert(tabname, {'a': '800000', 'b': "good", 'd': "bla", 'c': "black", 'e': 'Fuzzy wuzzy is a bear'})

        if verbose:
            self.tdb._db_print()

        # this should return two rows
        values = self.tdb.Select(tabname, ['b', 'a', 'd'],
            conditions={'e': re.compile('wuzzy').search, 'a': re.compile('^[0-9]+$').match})
        assert len(values) == 2

        # now lets delete one of them and try again
        self.tdb.Delete(tabname, conditions={'b': dbtables.ExactCond('good')})
        values = self.tdb.Select(tabname, ['a', 'd', 'b'], conditions={'e': dbtables.PrefixCond('Fuzzy')})
        assert len(values) == 1
        assert values[0]['d'] == None

        values = self.tdb.Select(tabname, ['b'],
            conditions={'c': lambda c: c == 'meep'})
        assert len(values) == 1
        assert values[0]['b'] == "bad"
        

    def test_CreateOrExtend(self):
        tabname = "test_CreateOrExtend"

        self.tdb.CreateOrExtendTable(tabname, ['name', 'taste', 'filling', 'alcohol content', 'price'])
        try:
            self.tdb.Insert(tabname, {'taste': 'crap', 'filling': 'no', 'is it Guinness?': 'no'})
            assert 0, "Insert should've failed due to bad column name"
        except:
            pass
        self.tdb.CreateOrExtendTable(tabname, ['name', 'taste', 'is it Guinness?'])

        # these should both succeed as the table should contain the union of both sets of columns.
        self.tdb.Insert(tabname, {'taste': 'crap', 'filling': 'no', 'is it Guinness?': 'no'})
        self.tdb.Insert(tabname, {'taste': 'great', 'filling': 'yes', 'is it Guinness?': 'yes', 'name': 'Guinness'})


    def test_CondObjs(self):
        tabname = "test_CondObjs"

        self.tdb.CreateTable(tabname, ['a', 'b', 'c', 'd', 'e', 'p'])

        self.tdb.Insert(tabname, {'a': "the letter A", 'b': "the letter B", 'c': "is for cookie"})
        self.tdb.Insert(tabname, {'a': "is for aardvark", 'e': "the letter E", 'c': "is for cookie", 'd': "is for dog"})
        self.tdb.Insert(tabname, {'a': "the letter A", 'e': "the letter E", 'c': "is for cookie", 'p': "is for Python"})

        values = self.tdb.Select(tabname, ['p', 'e'], conditions={'e': dbtables.PrefixCond('the l')})
        assert len(values) == 2, values
        assert values[0]['e'] == values[1]['e'], values
        assert values[0]['p'] != values[1]['p'], values

        values = self.tdb.Select(tabname, ['d', 'a'], conditions={'a': dbtables.LikeCond('%aardvark%')})
        assert len(values) == 1, values
        assert values[0]['d'] == "is for dog", values
        assert values[0]['a'] == "is for aardvark", values

        values = self.tdb.Select(tabname, None, {'b': dbtables.Cond(), 'e':dbtables.LikeCond('%letter%'), 'a':dbtables.PrefixCond('is'), 'd':dbtables.ExactCond('is for dog'), 'c':dbtables.PrefixCond('is for'), 'p':lambda s: not s})
        assert len(values) == 1, values
        assert values[0]['d'] == "is for dog", values
        assert values[0]['a'] == "is for aardvark", values


def suite():
    theSuite = unittest.TestSuite()
    theSuite.addTest(unittest.makeSuite(TableDBTestCase, 'test'))
    return theSuite

if __name__ == '__main__':
    if not unittest.TextTestRunner().run(suite()).wasSuccessful():
        sys.exit(1)
