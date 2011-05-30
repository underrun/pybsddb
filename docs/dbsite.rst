.. $Id$

==========
DBSite
==========

Read `Oracle documentation
<http://download.oracle.com/docs/cd/E17076_02/html/programmer_reference/group_membership.html>`__
for better understanding.

You use the DB_SITE handle to configure and manage replication sites.

`More info...
<http://download.oracle.com/docs/cd/E17076_02/html/api_reference/
C/repmgr_site.html>`__

DBSite Methods
------------------

.. function:: close(flags=0)

   Close a DBSite handle.
   `More info...
   <http://download.oracle.com/docs/cd/E17076_02/html/api_reference/
   C/dbsite_close.html>`__

.. function:: remove()

   Removes the site from the replication group. If called at the master
   site, repmgr updates the membership database directly. If called from
   a client, this method causes a request to be sent to the master to
   perform the operation. The method then awaits confirmation.
   `More info...
   <http://download.oracle.com/docs/cd/E17076_02/html/api_reference/
   C/dbsite_remove.html>`__


