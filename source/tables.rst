======
Tables
======

.. _conf-vars:

Table of Configuration Values
=============================

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Name
     - Since Minor
     - Type
     - Default
     - Units
   * - :ref:`asm-freq`
     - 0
     - ``uint32``
     - 600000
     - :abbr:`ms (milliseconds)`
   * - :ref:`asm-maxconn`
     - 0
     - ``uint32``
     - 50
     -
   * - :ref:`asm-minconn`
     - 0
     - ``uint32``
     - 3
     -
   * - :ref:`asm-qlen`
     - 0
     - ``uint32``
     - 5
     -
   * - :ref:`bcast-cache`
     - 0
     - ``uint32``
     - 600000
     - :abbr:`ms (milliseconds)`
   * - :ref:`ls-batch`
     - 0
     - ``uint32``
     - 5000
     - :abbr:`ms (milliseconds)`
   * - :ref:`ls-horizon`
     - 0
     - ``uint32``
     - 5
     -
   * - :ref:`ls-max`
     - 0
     - ``uint32``
     - 30000
     - :abbr:`ms (milliseconds)`
   * - :ref:`ls-regen`
     - 0
     - ``uint32``
     - 600000
     - :abbr:`ms (milliseconds)`
   * - :ref:`ping-freq`
     - 0
     - ``uint32``
     - 5000
     - :abbr:`ms (milliseconds)`
   * - :ref:`ping-lost`
     - 0
     - ``uint32``
     - 5
     -
   * - :ref:`ret-cnt`
     - 0
     - ``uint32``
     - 5
     -
   * - :ref:`ret-max`
     - 0
     - ``uint32``
     - 30000
     - :abbr:`ms (milliseconds)`

.. _protocols:

Table of Protocols
==================

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Name
     - Protocol Number
     - Since Minor
     - Sent From
     - Sent To
     - Message ID Fields
   * - :ref:`proto-negot`
     - 0
     - 0
     - Nodes; Clients
     - Nodes; Clients
     -
   * - :ref:`node-id-proto`
     - 1
     - 0
     - Nodes; Clients
     - Nodes; Clients
     -
   * - :ref:`ping-proto`
     - 2
     - 0
     - Nodes; Clients
     - Nodes; Clients
     - ``timestamp``
   * - :ref:`conf-proto`
     - 3
     - 0
     - Nodes; Admin Clients
     - Nodes; Clients
     - ``timestamp``
   * - :ref:`link-state-proto`
     - 10
     - 0
     - Nodes
     - Nodes; Admin Clients
     - ``sequence``, ``id``, ``generation``
   * - :ref:`node-disconnect-proto`
     - 15
     - 0
     - Nodes; Admin Clients
     - Nodes
     - ``id``, ``generation``, ``sequence``
   * - :ref:`client-disconnect-proto`
     - 16
     - 0
     - Nodes; Admin Clients
     - Nodes
     - ``source``, ``id``
   * - :ref:`admin-cmd-proto`
     - 20
     - 0
     - Admin Clients
     - Nodes
     - ``id``
   * - :ref:`link-subscription-proto`
     - 21
     - 0
     - Nodes
     - Admin Clients
     - ``id``
   * - :ref:`fwd-subscription-proto`
     - 22
     - 0
     - Nodes
     - Admin Clients
     - ``id``
   * - :ref:`gossip-subscription-proto`
     - 23
     - 0
     - Nodes
     - Admin Clients
     - ``id``
   * - :ref:`log-subscription-proto`
     - 24
     - 0
     - Nodes
     - Admin Clients
     - ``id``
