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
     - Type
     - Default
     - Units
   * - :ref:`asm-freq`
     - ``uint32``
     - 600000
     - :abbr:`ms (milliseconds)`
   * - :ref:`asm-maxconn`
     - ``uint32``
     - 50
     -
   * - :ref:`asm-minconn`
     - ``uint32``
     - 3
     -
   * - :ref:`asm-qlen`
     - ``uint32``
     - 5
     -
   * - :ref:`bcast-cache`
     - ``uint32``
     - 600000
     - :abbr:`ms (milliseconds)`
   * - :ref:`ls-batch`
     - ``uint32``
     - 5000
     - :abbr:`ms (milliseconds)`
   * - :ref:`ls-horizon`
     - ``uint32``
     - 5
     -
   * - :ref:`ls-max`
     - ``uint32``
     - 30000
     - :abbr:`ms (milliseconds)`
   * - :ref:`ls-regen`
     - ``uint32``
     - 600000
     - :abbr:`ms (milliseconds)`
   * - :ref:`ping-freq`
     - ``uint32``
     - 5000
     - :abbr:`ms (milliseconds)`
   * - :ref:`ping-lost`
     - ``uint32``
     - 5
     -
   * - :ref:`ret-cnt`
     - ``uint32``
     - 5
     -
   * - :ref:`ret-max`
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
   * - :ref:`proto-negot`
     - 0
     - 0
     - Nodes; Clients
     - Nodes; Clients
   * - :ref:`node-id-proto`
     - 1
     - 0
     - Nodes; Clients
     - Nodes; Clients
   * - :ref:`ping-proto`
     - 2
     - 0
     - Nodes; Clients
     - Nodes; Clients
   * - :ref:`conf-proto`
     - 3
     - 0
     - Nodes; Admin Clients
     - Nodes; Clients
   * - :ref:`link-state-proto`
     - 10
     - 0
     - Nodes
     - Nodes; Admin Clients
   * - :ref:`node-disconnect-proto`
     - 15
     - 0
     - Nodes; Admin Clients
     - Nodes
   * - :ref:`client-disconnect-proto`
     - 16
     - 0
     - Nodes; Admin Clients
     - Nodes
   * - :ref:`admin-cmd-proto`
     - 20
     - 0
     - Admin Clients
     - Nodes
   * - :ref:`link-subscription-proto`
     - 21
     - 0
     - Nodes
     - Admin Clients
   * - :ref:`fwd-subscription-proto`
     - 22
     - 0
     - Nodes
     - Admin Clients
   * - :ref:`gossip-subscription-proto`
     - 23
     - 0
     - Nodes
     - Admin Clients
   * - :ref:`log-subscription-proto`
     - 24
     - 0
     - Nodes
     - Admin Clients
