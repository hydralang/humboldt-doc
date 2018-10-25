.. index:: ! protocol; support
.. _support-proto:

=================
Support Protocols
=================

In this chapter, we discuss the support protocols.  Support protocols
are used to perform functions that *support* the Humboldt network:
measuring :abbr:`RTT (Round-Trip Time)`, disseminating information
about nodes, etc.  The support protocols are also the home of the
administrative client commands, which allow administrative clients to
control nodes and the network.

.. _node-id-proto:

Node ID Protocol
================

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Protocol Number
     - Since Minor
     - Sent From
     - Sent To
   * - 1
     - 0
     - Nodes; Clients
     - Nodes; Clients

The node ID protocol frame is exchanged immediately after conduit
establishment.  To facilitate protocol negotiation (see
:ref:`proto-negot`), no other encapsulated protocol frames are
exchanged until the node ID frame has been sent and acknowledged.  For
peer nodes, both peers must send and acknowledge this frame; for
clients, the node will send this frame and the client must acknowledge
it.

The node ID frame, described by the ``NodeID`` message, contains flags
that inform the recipient of the frame about the recipient's view of
the connection to the sender.  This includes information about whether
the recipient is a client, an administrative client, or a peer, as
well as the protections afforded by the security layer.  In addition
to this, peer nodes will always include that node's 128-bit
:ref:`node-id` and :ref:`generation-id`, and if the recipient of the
frame is a client, the :ref:`client-id`.  Finally, the sender of the
node ID frame always includes the highest supported minor version of
the Humboldt protocol.  The :term:`protobuf` definition is as follows:

.. literalinclude:: protobuf/node_id.proto
   :language: proto
   :lines: 7-30
   :lineno-match:
   :caption: :download:`node_id.proto <protobuf/node_id.proto>`

For peer nodes, the acknowledgment, described by ``NodeIDAck``, does
not need to contain any data.  However, Humboldt clients do not send
the node ID frame, and so they need to provide the Humboldt node they
connect to with the highest minor version of the Humboldt protocol
they support.  This makes the :term:`protobuf` definition look like:

.. literalinclude:: protobuf/node_id.proto
   :language: proto
   :lines: 32-40
   :lineno-match:
   :caption: :download:`node_id.proto <protobuf/node_id.proto>`

.. _ping-proto:

Ping Protocol
=============

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Protocol Number
     - Since Minor
     - Sent From
     - Sent To
   * - 2
     - 0
     - Nodes; Clients
     - Nodes; Clients

The ping protocol frames are exchanged to validate aliveness of
directly linked peer nodes and to measure the :abbr:`RTT (Round-Trip
Time)` to those nodes for routing computations.  As pings are
exchanged frequently, this protocol frame is also made responsible for
exchanging :term:`rumors` regarding linked nodes.  A given Humboldt
node sends the ``Ping`` message to every one of its links at an
interval described by :ref:`ping-freq`, though note that it is
recommended that a node stagger the sending of ping messages among all
its peer nodes, in order to avoid overloading its local network.  The
node expects its peer to reply with a ``Pong`` message.  A node
considers a connection lost if more than :ref:`ping-lost` consecutive
pongs are not received from the peer.

The ``Ping`` message's :term:`protobuf` definition is as follows:

.. literalinclude:: protobuf/ping.proto
   :language: proto
   :lines: 8-16
   :lineno-match:
   :caption: :download:`ping.proto <protobuf/ping.proto>`

In addition to a 64-bit millisecond-resolution timestamp, the ``Ping``
message also contains a ``NodeRumor``, described as follows:

.. literalinclude:: protobuf/rumor.proto
   :language: proto
   :lines: 7-15
   :lineno-match:
   :caption: :download:`rumor.proto <protobuf/rumor.proto>`

This message, in turn, contains a list of ``Conduit`` messages, each
of which describe a way to connect to the node the rumor is about:

.. literalinclude:: protobuf/conduit.proto
   :language: proto
   :lines: 5-9
   :lineno-match:
   :caption: :download:`conduit.proto <protobuf/conduit.proto>`

A Humboldt node that receives a ``Ping`` message **MUST** reply with a
``Pong`` message, with the same timestamp it received in the
``Ping``.  It may optionally include a ``NodeRumor``, as in the
``Ping`` message, but it is **RECOMMENDED** that the node pre-select a
node prior to receiving the ``Ping``, to facilitate quick
turn-around.  The ``Pong`` message looks like:

.. literalinclude:: protobuf/ping.proto
   :language: proto
   :lines: 18-29
   :lineno-match:
   :caption: :download:`ping.proto <protobuf/ping.proto>`

.. note::

   The ``NodeRumor`` message **MUST NOT** be included in ``Ping``
   messages sent to clients; likewise, a ``NodeRumor`` message
   included in a ``Pong`` received from any client **MUST** be
   ignored.  In client exchanges, the timestamp is **OPTIONAL**, as
   nodes generally do not care about :abbr:`RTT (Round-Trip Time)` to
   clients.

   Clients **MAY** send ``Ping`` messages to Humboldt nodes, for the
   same reason that nodes send them to clients: to verify aliveness of
   the connection.  The node **MUST** reply with ``Pong`` messages,
   but it **MAY** also apply rate-limiting controls.

.. important::

   To prevent reflection attacks utilizing Humboldt, nodes **MUST
   NOT** reply to ``Ping`` messages unless those messages are
   associated with a currently active conduit.
