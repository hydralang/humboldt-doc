====================================
Network-wide Configuration Variables
====================================

There are a number of common configuration values that are used by
Humboldt, and which must be common for each :term:`node` on the
network.  This document contains the list of variables, the value type
of each, the default if not present, and the units for interpreting
that value (if applicable), as well as a brief description of the
meaning of each variable.

Variables
=========

.. _ret-cnt:

``RET_CNT``
-----------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Type
     - Default
     - Units
   * - ``uint32``
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

   * - Type
     - Default
     - Units
   * - ``uint32``
     - 30000
     - :abbr:`ms (milliseconds)`

The ``RET_MAX`` configuration variable gives the maximum
retransmission timeout.  Exponential backoff will stop increasing the
timeout once this value is reached.
