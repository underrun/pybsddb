.. $Id$

=====
DBTxn
=====

DBTxn Methods
-------------

.. function:: abort()

   Aborts the transaction
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/txn_abort.html>`__

.. function:: commit(flags=0)

   Ends the transaction, committing any changes to the databases.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/txn_commit.html>`__

.. function:: id()

   The txn_id function returns the unique transaction id associated with
   the specified transaction.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/txn_id.html>`__

.. function:: prepare(gid)

   Initiates the beginning of a two-phase commit. Begining with
   BerkeleyDB 3.3 a global identifier paramater is required, which is a
   value unique across all processes involved in the commit. It must be
   a string of DB_XIDDATASIZE bytes.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/txn_prepare.html>`__


