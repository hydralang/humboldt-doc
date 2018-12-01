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
frame is a client, the :ref:`client-id`.  The sender of the node ID
frame **MUST** always includes the highest supported minor version of
the Humboldt protocol.  Finally, the node ID frame **MAY** contain a
free-form implementation tag that describes the node's implementation.
The :term:`protobuf` definition is as follows:

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

   Peer nodes exchange ``Ping`` messages immediately after exchanging
   node ID information (see :ref:`node-id-proto`) in order to create
   an initial :abbr:`RTT (Round-Trip Time)` measurement for the link
   state protocol.  The conduit is not considered active until at
   least one ``Pong`` message has been received by the node.

.. _conf-proto:

Configuration Protocol
======================

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Protocol Number
     - Since Minor
     - Sent From
     - Sent To
   * - 3
     - 0
     - Nodes; Admin Clients
     - Nodes; Clients

The configuration protocol frames are exchanged immediately after
exchanging node ID information.  They are also exchanged, in a
broadcast, whenever an administrative client updates the
configuration.

Configuration variable names consist of a dotted sequence of
identifiers (which **SHOULD** match the regular expression
``/^[a-zA-Z_][a-zA-Z0-9_]*$/``).  All configuration variables consumed
by the Humboldt network itself contain no dots, e.g.,
:ref:`ping-freq`.  If applications utilizing Humboldt choose to
utilize the configuration protocol, it is **RECOMMENDED** that they
choose a unique dotted prefix to use for their variables, e.g.,
"com.example.var1", "com.example.var2", etc.  Configuration variable
values may be strings, integers (of at most 32 bits), or booleans; all
configuration variables **MUST** have a reasonable default that will
be used if the variable does not appear in the ``Variables`` message.
For more on the Humboldt-specific configuration variables, see
:ref:`conf-vars-list`.

The ``Variables`` message contains the set of non-default variables
and their values, as well as a millisecond-resolution timestamp that
serves to identify the variable version.  The :term:`protobuf`
definition is as follows:

.. literalinclude:: protobuf/configuration.proto
   :language: proto
   :lines: 7-28
   :lineno-match:
   :caption: :download:`configuration.proto <protobuf/configuration.proto>`

A node receiving a ``Variables`` message **MUST** respond with a
``VariablesAck`` message with the same timestamp.  If the received
timestamp is less than or equal to that of the current configuration
known by the node, no other action is taken; otherwise, the node
updates its current configuration and forwards the ``Variables`` frame
as a broadcast (see :ref:`broadcast`).  The ``VariablesAck`` message
is defined as follows:

.. literalinclude:: protobuf/configuration.proto
   :language: proto
   :lines: 30-37
   :lineno-match:
   :caption: :download:`configuration.proto <protobuf/configuration.proto>`

.. important::

   Peer nodes exchange ``Variables`` messages immediately after
   exchanging node ID information (see :ref:`node-id-proto`); nodes
   also send a ``Variables`` message to clients when those clients
   connect.  The conduit is not considered active until the
   ``VariablesAck`` message has been received by the node.  However,
   nodes **MUST** ignore ``Variables`` messages sent by clients,
   unless the client is an administrative client and the conduit is
   already considered active.

.. _link-state-proto:

Link State Protocol
===================

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Protocol Number
     - Since Minor
     - Sent From
     - Sent To
   * - 10
     - 0
     - Nodes
     - Nodes; Admin Clients

.. sidebar:: Debouncing

   A given event could occur multiple times in succession.  For
   instance, a network anomaly could cause multiple peers to
   disconnect in quick succession.  If a Humboldt node generated a new
   link state protocol frame for each of these events, several such
   frames could be generated in quick succession, all with different
   sequence numbers.  To mitigate this effect, Humboldt nodes **MUST**
   implement the :ref:`debouncing-algorithm` for this case.  The
   duration of the shorter duration timer is given by :ref:`ls-batch`,
   and the longer timer by :ref:`ls-max`.  (Note: these same values
   are also used by the logic that triggers routing table computation;
   see :ref:`link-state-algorithm` for more information.)

The link state protocol is responsible for distributing routing
information throughout the Humboldt network.  A node generates and
broadcasts a link state protocol frame whenever a link :abbr:`RTT
(Round Trip Time)` has changed by more than 10 percent; whenever a
link is lost or a new link has reached the active state; or
periodically, at a time interval specified by the :ref:`ls-regen`
configuration value.  It is **REQUIRED** that Humboldt implementations
use :term:`debouncing` logic to batch updates; see the sidebar for
more information.

A link state protocol frame, described by the ``LinkState`` message,
contains the :ref:`node-id` and :ref:`generation-id` of the node that
generated it.  It must also contain a *sequence number*, which is to
be incremented each time a new link state protocol frame is generated
by that node.  The link state protocol frame will also contain the
list of conduit URIs that the node listens on and information about
all of the links (or *neighbors*) that node has to its peers, and the
optional implementation tag for the node.

Link state protocol frames are broadcast to all nearby nodes.  To
ensure that these messages don't traverse the entire network, the
broadcast is limited by including a "max_hops" field, which is
initialized from the :ref:`ls-horizon` configuration value.  Each
node, before retransmitting the frame, **MUST** decrement the
"max_hops" field and, if it reaches 0, **MUST NOT** forward the frame.

The node neighbors are described in the link state protocol frame with
``Neighbor`` messages, which need only contain the neighbor's ID and
the smoothed :abbr:`RTT (Round-Trip Time)`.  For auditing purposes,
these messages also contain the link principal (if known; see
:ref:`security-layer`) and the conduit URIs for both ends of the link;
administrative clients can use this data to check for suspicious
links.

The ``Neighbor`` and ``LinkState`` messages are defined as follows:

.. literalinclude:: protobuf/link_state.proto
   :language: proto
   :lines: 8-36
   :lineno-match:
   :caption: :download:`link_state.proto <protobuf/link_state.proto>`

The ``Conduit`` message is defined the same as for the
:ref:`ping-proto`:

.. literalinclude:: protobuf/conduit.proto
   :language: proto
   :lines: 5-9
   :lineno-match:
   :caption: :download:`conduit.proto <protobuf/conduit.proto>`

Finally, the ``LinkState`` message must be acknowledged, hop-by-hop,
with a ``LinkStateAck`` message:

.. literalinclude:: protobuf/link_state.proto
   :language: proto
   :lines: 38-47
   :lineno-match:
   :caption: :download:`link_state.proto <protobuf/link_state.proto>`

.. note::

   When a link state protocol frame is regenerated due to the
   :ref:`ls-regen` timer expiring, the new link state protocol frame
   **MUST** be generated with the most recent available information
   for the :abbr:`RTT (Round-Trip Time)` of all links.

.. _admin-cmd-proto:

Administrative Command Protocol
===============================

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Protocol Number
     - Since Minor
     - Sent From
     - Sent To
   * - 20
     - 0
     - Admin Clients
     - Nodes

The administrative command protocol provides a means of administrating
a single Humboldt node.  Administrative clients may use this protocol
to instruct the node to perform a number of tasks, including shutting
down, connecting to another node, or retrieving data.  Administrative
clients may also use commands to subscribe to certain network data
that may change over time, but which most clients would not be
interested in, such as link state frames.

A ``CommandRequest`` message is used to send the command to the node.
This message includes a client-generated ID, which may be used by the
client to differentiate responses in the face of multiple in-flight
commands.  The commands may be any value from the ``Command``
enumeration (and are described in subsections below).  (Implementation
specific commands can be specified as well; the range of enumeration
values starting at 50000 is reserved for this purpose.)  Some commands
may require arguments; the ``CommandRequest`` message uses the
``CommandArgument`` message for each of the arguments.  The
``Command`` enumeration and ``CommandArgument`` and ``CommandRequest``
messages are defined as follows:

.. literalinclude:: protobuf/admin.proto
   :language: proto
   :lines: 8-48
   :lineno-match:
   :caption: :download:`admin.proto <protobuf/admin.proto>`

.. note::

   All commands, including implementation-specific commands, **MUST**
   be idempotent.  Nodes **MAY** use the client-generated ID to ensure
   that commands are not executed multiple times in the face of packet
   loss, but it is **RECOMMENDED** that commands be constructed in
   such a fashion that they are inherently idempotent; for example, a
   subscription command **SHOULD** take a boolean value indicating
   whether to subscribe or unsubscribe.

The Humboldt node **MUST** respond to a ``CommandRequest`` message
with either a ``CommandResponse`` or ``CommandError`` message, as
appropriate; these messages are defined as follows:

.. literalinclude:: protobuf/admin.proto
   :language: proto
   :lines: 50-75
   :lineno-match:
   :caption: :download:`admin.proto <protobuf/admin.proto>`

In either case, the ID **MUST** match the ID provided by the client in
the ``CommandRequest`` message.  In the ``CommandError`` message, a
numerical code provides a computer-readable indication of the error,
and a human-readable, UTF-8 encoded string is provided for display to
the user.

.. note::

   As with the protocol 0 ``ERR`` frame, it is **NOT RECOMMENDED**
   that this error message be localized; these errors should be in
   English to facilitate web searches for the error message.

.. _noop-cmd:

The ``NOOP`` Command
--------------------

The ``NOOP`` command does nothing.  It takes no arguments and produces
no results.  It provides an additional way for a client to confirm
that it has administrative privileges.  This command really exists
because enumerations always default to 0.

.. _shutdown-cmd:

The ``SHUTDOWN`` Command
------------------------

The ``SHUTDOWN`` command causes the Humboldt node to shut down
cleanly.  It takes no arguments and produces no results.  The node
**MUST** generate the ``CommandResponse`` prior to shutting down, but
clients are warned that operating system-level buffering may result in
the ``CommandResponse`` message being lost.

.. _connect-cmd:

The ``CONNECT`` Command
-----------------------

The ``CONNECT`` command is used to instruct the Humboldt node to
connect to another node.  This mechanism is provided to allow a node
to connect to at least one other network node, after which the
:ref:`self-assembly` algorithm can take over.

The arguments to the ``CONNECT`` command must be a sequence of
canonical :ref:`conduit-uri` strings.  The ``CommandResponse`` message
will contain no results, and simply indicates receipt of the command;
the connection will be queued by the Humboldt instance, as described
in :ref:`self-assembly`.

.. _link-subscribe-cmd:

The ``LINK_SUBSCRIBE`` Command
------------------------------

The ``LINK_SUBSCRIBE`` command is used to instruct the Humboldt node
to start or stop sending :ref:`link-subscription-proto` frames to the
client.  The ``CommandRequest`` will include a single boolean
argument; if ``true``, the client will be subscribed.  Likewise, the
``CommandResponse`` will include a boolean result indicating the state
of the subscription.

.. _ls-subscribe-cmd:

The ``LS_SUBSCRIBE`` Command
----------------------------

The ``LS_SUBSCRIBE`` command is used to instruct the Humboldt node to
start or stop sending :ref:`link-state-proto` frames to the client.
The ``CommandRequest`` will include a single boolean argument; if
``true``, the client will be subscribed.  Likewise, the
``CommandResponse`` will include a boolean result indicating the state
of the subscription.

When a client is subscribed to link state protocol frames, it will
receive all the frames *as sent by the node*, that is, after the
decrement of the ``max_hops`` field.  However, all the frames will be
forwarded to a subscribed client, even ones for which ``max_hops`` has
been decremented to 0.  In conjunction with the :ref:`ls-table-cmd`,
this allows the client to synchronize with the node's link state
table.

.. _fwd-subscribe-cmd:

The ``FWD_SUBSCRIBE`` Command
-----------------------------

The ``FWD_SUBSCRIBE`` command is used to instruct the Humboldt node to
start or stop sending :ref:`fwd-subscription-proto` frames to the
client.  The ``CommandRequest`` will include a single boolean
argument; if ``true``, the client will be subscribed.  Likewise, the
``CommandResponse`` will include a boolean result indicating the state
of the subscription.

When a client is subscribed to forward table subscription protocol
frames, it will receive a frame each time the forwarding table is
regenerated.

.. _gos-subscribe-cmd:

The ``GOS_SUBSCRIBE`` Command
-----------------------------

The ``GOS_SUBSCRIBE`` command is used to instruct the Humboldt node to
start or stop sending :ref:`gossip-subscription-proto` frames to the
client.  The ``CommandRequest`` will include a single boolean
argument; if ``true``, the client will be subscribed.  Likewise, the
``CommandResponse`` will include a boolean result indicating the state
of the subscription.

When a client is subscribed to gossip subscription protocol frames, it
will receive frames for all other Humboldt nodes that the connected
node learns about through the gossip protocol.  If the node already
knows about the other node, including through the gossip protocol,
that will not be passed on to the subscribed client.

.. _log-subscribe-cmd:

The ``LOG_SUBSCRIBE`` Command
-----------------------------

The ``LOG_SUBSCRIBE`` command is used to instruct the Humboldt node to
start or stop sending :ref:`log-subscription-proto` frames to the
client.  The ``CommandRequest`` will include a single boolean
argument; if ``true``, the client will be subscribed.  Likewise, the
``CommandResponse`` will include a boolean result indicating the state
of the subscription.

When a client is subscribed to log subscription protocol frames, the
Humboldt node **MUST NOT** send log messages related to that client.
This precaution avoids the possibility of a log message explosion due
to a subscribed client.

.. note::

   It is **NOT RECOMMENDED** that log messages be localized; these
   messages should be in English to facilitate web searches for the
   log message.

.. caution::

   Clients are warned that different implementations may have very
   different log messages, different logging frequencies, and
   different log filtering.  The protocol does not include any means
   of adjusting the filtering an implementation uses; if such
   adjustment is provided by an implementation, it is **RECOMMENDED**
   that it be provided through an extension command.

.. _links-cmd:

The ``LINKS`` Command
---------------------

The ``LINKS`` command is used to retrieve a list of all of the
Humboldt node's current links.  The request takes no arguments, and
the response will contain, for each link, a ``Link`` message
describing the link.  This message is defined as follows:

.. literalinclude:: protobuf/link.proto
   :language: proto
   :lines: 5-24
   :lineno-match:
   :caption: :download:`link.proto <protobuf/link.proto>`

.. _ls-table-cmd:

The ``LS_TABLE`` Command
------------------------

The ``LS_TABLE`` command is used to retrieve the Humboldt node's link
state table, consisting of all the link state protocol frames that
have been received by the node.  The request takes no arguments, and
the results will contain, for each link state protocol frame, a
``LinkState`` message, as defined in :ref:`link-state-proto`.

.. _fwd-table-cmd:

The ``FWD_TABLE`` Command
-------------------------

The ``FWD_TABLE`` command is used to retrieve the Humboldt node's
forwarding table, as computed using the :ref:`link-state-algorithm`.
The request takes no arguments, and the results will contain, for each
entry in the forwarding table, a ``ForwardTo`` message defined as
follows:

.. literalinclude:: protobuf/forward.proto
   :language: proto
   :lines: 5-11
   :lineno-match:
   :caption: :download:`forward.proto <protobuf/forward.proto>`

.. _gos-table-cmd:

The ``GOS_TABLE`` Command
-------------------------

The ``GOS_TABLE`` command is used to retrieve the Humboldt node's
gossip table.  This table includes all nodes that the Humboldt node
*only* knows about due to the gossip exchange (see :ref:`ping-proto`
for more information).  The request takes no arguments, and the
results will contain, for each entry in the table, a ``NodeRumor``.
(Again, see :ref:`ping-proto` for the definition of this message.)
