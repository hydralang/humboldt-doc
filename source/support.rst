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

The node ID frame contains flags that inform the recipient of the
frame about the recipient's view of the connection to the sender.
This includes information about whether the recipient is a client, an
administrative client, or a peer, as well as the protections afforded
by the security layer.  In addition to this, peer nodes will always
include that node's 128-bit :ref:`node-id` and :ref:`generation-id`,
and if the recipient of the frame is a client, the :ref:`client-id`.
Finally, the sender of the node ID frame always includes the highest
supported minor version of the Humboldt protocol.  The
:term:`protobuf` definition is as follows:

.. literalinclude:: protobuf/node_id.proto
   :language: proto
   :lines: 7-30
   :lineno-match:
   :caption: :download:`node_id.proto <protobuf/node_id.proto>`

For peer nodes, the acknowledgment does not need to contain any data.
However, Humboldt clients do not send the node ID frame, and so they
need to provide the Humboldt node they connect to with the highest
minor version of the Humboldt protocol they support.  This makes the
:term:`protobuf` definition look like:

.. literalinclude:: protobuf/node_id.proto
   :language: proto
   :lines: 32-40
   :lineno-match:
   :caption: :download:`node_id.proto <protobuf/node_id.proto>`
