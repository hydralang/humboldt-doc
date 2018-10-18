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
   * - :ref:`bcast-cache`
     - ``uint32``
     - 600000
     - :abbr:`ms (milliseconds)`
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
     - Number
     - Since Minor
     - Uses ``REP``
     - Uses ``ERR``
     - Uses ``REP`` and ``ERR``
   * - :ref:`proto-negot`
     - 0
     - 0
     -
     - Y
     -
