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
     - Protobuf Files
   * - :ref:`proto-negot`
     - 0
     - 0
     - Nodes; Clients
     - Nodes; Clients
     -
     -
   * - :ref:`node-id-proto`
     - 1
     - 0
     - Nodes; Clients
     - Nodes; Clients
     -
     - :download:`node_id.proto <protobuf/node_id.proto>`
   * - :ref:`ping-proto`
     - 2
     - 0
     - Nodes; Clients
     - Nodes; Clients
     - ``timestamp``
     - :download:`ping.proto <protobuf/ping.proto>`
       :download:`rumor.proto <protobuf/rumor.proto>`
       :download:`conduit.proto <protobuf/conduit.proto>`
   * - :ref:`conf-proto`
     - 3
     - 0
     - Nodes; Admin Clients
     - Nodes; Clients
     - ``timestamp``
     - :download:`configuration.proto <protobuf/configuration.proto>`
   * - :ref:`link-state-proto`
     - 10
     - 0
     - Nodes
     - Nodes; Admin Clients
     - ``sequence``, ``id``, ``generation``
     - :download:`link_state.proto <protobuf/link_state.proto>`
       :download:`conduit.proto <protobuf/conduit.proto>`
   * - :ref:`node-disconnect-proto`
     - 15
     - 0
     - Nodes; Admin Clients
     - Nodes
     - ``id``, ``generation``, ``sequence``
     - :download:`disconnect.proto <protobuf/disconnect.proto>`
   * - :ref:`client-disconnect-proto`
     - 16
     - 0
     - Nodes; Admin Clients
     - Nodes
     - ``source``, ``id``
     - :download:`client_disconnect.proto
       <protobuf/client_disconnect.proto>`
   * - :ref:`admin-cmd-proto`
     - 20
     - 0
     - Admin Clients
     - Nodes
     - ``id``
     - :download:`admin.proto <protobuf/admin.proto>`
       :download:`link.proto <protobuf/link.proto>`
       :download:`link_state.proto <protobuf/link_state.proto>`
       :download:`conduit.proto <protobuf/conduit.proto>`
       :download:`forward.proto <protobuf/forward.proto>`
       :download:`rumor.proto <protobuf/rumor.proto>`
   * - :ref:`link-subscription-proto`
     - 21
     - 0
     - Nodes
     - Admin Clients
     - ``id``
     - :download:`link_sub.proto <protobuf/link_sub.proto>`
       :download:`link.proto <protobuf/link.proto>`
   * - :ref:`fwd-subscription-proto`
     - 22
     - 0
     - Nodes
     - Admin Clients
     - ``id``
     - :download:`forward_sub.proto <protobuf/forward_sub.proto>`
       :download:`forward.proto <protobuf/forward.proto>`
   * - :ref:`gossip-subscription-proto`
     - 23
     - 0
     - Nodes
     - Admin Clients
     - ``id``
     - :download:`gossip_sub.proto <protobuf/gossip_sub.proto>`
       :download:`rumor.proto <protobuf/rumor.proto>`
       :download:`conduit.proto <protobuf/conduit.proto>`
   * - :ref:`log-subscription-proto`
     - 24
     - 0
     - Nodes
     - Admin Clients
     - ``id``
     - :download:`log_sub.proto <protobuf/log_sub.proto>`
