========
Humboldt
========

Overview
========

Humboldt is a highly-scalable, self-assembling :term:`overlay network`
that provides :term:`unicast`, :term:`anycast`, :term:`multicast`,
:term:`broadcast`, and network-wide configuration services within the
network.  A given Humboldt instance (called a :term:`node` or
:term:`peer`) can connect to any other peer in the network, and will
automatically set up appropriately redundant links with no further
intervention by the administrator.  Humboldt nodes have local
configuration that is used to configure link security, and
network-wide configuration that can be altered by an administrative
client.

.. attention::

   The network-wide configuration service is targeted at Humboldt
   itself.  Other applications can leverage this service, but only
   administrative clients can alter the configuration, and the design
   of this service is optimized for rarely updated data, such as
   configuration.

.. note::

   Humboldt is more of a protocol than it is any given implementation
   of that protocol.  This documentation is intended to describe the
   Humboldt concept and protocol.  See the documentation for your
   implementation for specifics related to that implementation.

.. important::

   The key words "**MUST**", "**MUST NOT**", "**REQUIRED**",
   "**SHALL**", "**SHALL NOT**", "**SHOULD**", "**SHOULD NOT**",
   "**RECOMMENDED**", "**NOT RECOMMENDED**", "**MAY**", and
   "**OPTIONAL**" in this documentation are to be interpreted as
   described in :rfc:`2119` and :rfc:`8174` when, and only when, they
   appear in all capitals, as shown here.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   high-level
   glossary

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
