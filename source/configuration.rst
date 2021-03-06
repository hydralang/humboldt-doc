====================================
Network-wide Configuration Variables
====================================

There are a number of common configuration values that are used by
Humboldt, and which must be common for each :term:`node` on the
network.  This document contains the list of variables, the value type
of each, the default if not present, and the units for interpreting
that value (if applicable), as well as a brief description of the
meaning of each variable.

.. _conf-vars-list:

Variables
=========

.. _asm-freq:

``ASM_FREQ``
------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Since Minor
     - Type
     - Default
     - Units
   * - 0
     - ``uint32``
     - 600000
     - :abbr:`ms (milliseconds)`

The ``ASM_FREQ`` configuration variable gives the length of each round
of the self-assembly algorithm.

.. _asm-maxconn:

``ASM_MAXCONN``
---------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Since Minor
     - Type
     - Default
     - Units
   * - 0
     - ``uint32``
     - 50
     -

The ``ASM_MAXCONN`` configuration variable provides the "maximum"
number of connections a Humboldt node will attempt to open.  The
"maximum" is in quotes because this is a soft limit controlling
probability only; a Humboldt node may make or attempt to make any
number of connections, depending on the needs of the self-assembly
algorithm.

.. _asm-minconn:

``ASM_MINCONN``
---------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Since Minor
     - Type
     - Default
     - Units
   * - 0
     - ``uint32``
     - 3
     -

The ``ASM_MINCONN`` configuration variable governs the minimum number
of connections a node is allowed to have.  If the total number of
connections is less than this value, the node **MUST** attempt to
initiate enough connections per round to bring the connection count up
to this value.

.. _asm-qlen:

``ASM_QLEN``
------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Since Minor
     - Type
     - Default
     - Units
   * - 0
     - ``uint32``
     - 5
     -

The ``ASM_QLEN`` configuration variable controls the maximum number of
outgoing connections a node may seek at once.

.. _bcast-cache:

``BCAST_CACHE``
---------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Since Minor
     - Type
     - Default
     - Units
   * - 0
     - ``uint32``
     - 600000
     - :abbr:`ms (milliseconds)`

The ``BCAST_CACHE`` configuration variable gives the maximum amount of
time to store a broadcast frame's ID.

.. _ls-batch:

``LS_BATCH``
------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Since Minor
     - Type
     - Default
     - Units
   * - 0
     - ``uint32``
     - 5000
     - :abbr:`ms (milliseconds)`

The length of the shorter duration timer used for :term:`debouncing`
in the link state protocol and algorithm (see
:ref:`link-state-algorithm` and :ref:`link-state-proto`).  For more on
debouncing, see :ref:`debouncing-algorithm`.

.. _ls-horizon:

``LS_HORIZON``
--------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Since Minor
     - Type
     - Default
     - Units
   * - 0
     - ``uint32``
     - 5
     -

The horizon for the link state routing algorithm.  A given link state
protocol frame may transit at most this many hops, in order to limit
the memory footprint of Humboldt nodes.

.. _ls-max:

``LS_MAX``
----------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Since Minor
     - Type
     - Default
     - Units
   * - 0
     - ``uint32``
     - 30000
     - :abbr:`ms (milliseconds)`

The length of the longer duration timer used for :term:`debouncing` in
the link state protocol and algorithm (see :ref:`link-state-algorithm`
and :ref:`link-state-proto`).  For more on debouncing, see
:ref:`debouncing-algorithm`.

.. _ls-regen:

``LS_REGEN``
------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Since Minor
     - Type
     - Default
     - Units
   * - 0
     - ``uint32``
     - 600000
     - :abbr:`ms (milliseconds)`

The frequency with which link state protocol frames are regenerated,
regardless of changes to the link state.

.. _ping-freq:

``PING_FREQ``
-------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Since Minor
     - Type
     - Default
     - Units
   * - 0
     - ``uint32``
     - 5000
     - :abbr:`ms (milliseconds)`

Frequency with which ping messages are sent; see :ref:`ping-proto`.
Should be kept short to help ensure that node gossip spreads around
the network in a timely manner.

.. _ping-lost:

``PING_LOST``
-------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Since Minor
     - Type
     - Default
     - Units
   * - 0
     - ``uint32``
     - 5
     -

Maximum number of contiguous lost pings before a Humboldt node decides
the connection has been lost and closes it.

.. _ret-cnt:

``RET_CNT``
-----------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Since Minor
     - Type
     - Default
     - Units
   * - 0
     - ``uint32``
     - 5
     -

The ``RET_CNT`` configuration variable gives the maximum number of
retransmissions to attempt.

.. _ret-max:

``RET_MAX``
-----------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Since Minor
     - Type
     - Default
     - Units
   * - 0
     - ``uint32``
     - 30000
     - :abbr:`ms (milliseconds)`

The ``RET_MAX`` configuration variable gives the maximum
retransmission timeout.  Exponential backoff will stop increasing the
timeout once this value is reached.
