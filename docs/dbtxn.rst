.. $Id$

=====
DBTxn
=====

DBTxn Methods
-------------

.. function:: abort()

   Aborts the transaction
   `More info...
   <http://download.oracle.com/docs/cd/E17076_02/html/api_reference/
   C/txnabort.html>`__

.. function:: commit(flags=0)

   Ends the transaction, committing any changes to the databases.
   `More info...
   <http://download.oracle.com/docs/cd/E17076_02/html/api_reference/
   C/txncommit.html>`__

.. function:: id()

   The txn_id function returns the unique transaction id associated with
   the specified transaction.
   `More info...
   <http://download.oracle.com/docs/cd/E17076_02/html/api_reference/
   C/txnid.html>`__

.. function:: prepare(gid)

   Initiates the beginning of a two-phase commit. A global identifier
   parameter is required, which is a value unique across all processes
   involved in the commit. It must be a string of DB_GID_SIZE bytes.
   `More info...
   <http://download.oracle.com/docs/cd/E17076_02/html/api_reference/
   C/txnprepare.html>`__

.. function:: discard()

   This method frees up all the per-process resources associated with
   the specified transaction, neither committing nor aborting the
   transaction. The transaction will be keep in "unresolved" state. This
   call may be used only after calls to "dbenv.txn_recover()". A
   "unresolved" transaction will be returned again thru new calls to
   "dbenv.txn_recover()".
   
   For example, when there are multiple global transaction managers
   recovering transactions in a single Berkeley DB environment, any
   transactions returned by "dbenv.txn_recover()" that are not handled
   by the current global transaction manager should be discarded using
   "txn.discard()".

   `More info...
   <http://download.oracle.com/docs/cd/E17076_02/html/api_reference/
   C/txndiscard.html>`__

.. function:: set_timeout(timeout, flags)

   Sets timeout values for locks or transactions for the specified
   transaction.
   `More info...
   <http://download.oracle.com/docs/cd/E17076_02/html/api_reference/
   C/txnset_timeout.html>`__

.. function:: get_name(name)

   Returns the string associated with the transaction.
   `More info...
   <http://download.oracle.com/docs/cd/E17076_02/html/api_reference/
   C/txnset_name.html>`__

.. function:: set_name(name)

   Associates the specified string with the transaction.
   `More info...
   <http://download.oracle.com/docs/cd/E17076_02/html/api_reference/
   C/txnset_name.html>`__

