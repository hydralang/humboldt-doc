========================
Humboldt Protocol Basics
========================

.. index:: ! frame
.. index:: ! carrier protocol

Humboldt Frames
===============

The Humboldt protocol is a layered protocol, capable of carrying
several different payloads.  The first concept to understand about the
protocol is the nature of its :term:`protocol data unit`, or PDU.
Since the Humboldt protocol is intended to be usable with both TCP and
UDP, the PDU must be able to accommodate being sent over both
transports.  With UDP, this is trivial: one :term:`frame` per UDP
datagram.  However, TCP provides a stream-oriented protocol, which
implies that the Humboldt protocol must provide the structure
necessary to split that otherwise undifferentiated stream of data into
a series of frames.

Humboldt does this with what it calls the :term:`carrier protocol`.
The carrier protocol must be designed to provide the framing
information, as well as such things as protocol version and frame
contents, with as little overhead as possible.  As such, the protocol
is designed to use a simple 4-byte header, laid out like so:

.. literalinclude:: ../build/bits/carrier.txt
   :language: none

The field labeled "Vers." consists of a 4-bit protocol version.  This
indicates the version of the entire Humboldt protocol; this
documentation describes version 0.  (See :ref:`proto-negot` for more
on Humboldt protocol versioning.)  The next two bits are flag bits,
used to modify the :term:`encapsulated protocol`; in general, the
``REP`` flag indicates a reply, and ``ERR`` indicates an error report.
The two bits following the flag bits are reserved, and **MUST** be set
to 0.

The "Protocol" field contains an 8-bit protocol number.  The protocol
number space is split into two parts: protocol numbers from 1 to 127
are assigned to encapsulated protocols, while protocol numbers from
128 through 255 are intended to identify *extensions* to the carrier
protocol.  (Protocol number 0 is reserved for reporting link errors
and for protocol version negotiation; see :ref:`proto-negot`.)
Finally, the "Total Frame Length" field is, as the name suggests, a
16-bit byte length which includes the frame header.

.. index:: ! carrier protocol; extensions

Carrier Protocol Extensions
---------------------------

The carrier protocol design is inspired by the design of IPv6; in that
protocol, the protocol number space is split up to identify
:term:`extensions` vs. encapsulated protocols; extensions form a chain
of headers, with each header indicating the disposition of the packet
should the extension not be understood, as well as the length of the
extension header so that the protocol processor may skip it.  Humboldt
uses the exact same mechanism, with another 4-byte header per
extension, laid out like so:

.. literalinclude:: ../build/bits/carrier.txt
   :language: none

This format begins with 3 flag bits, which describe the disposition of
the frame and the extension in the case that it is not known to the
receiving :term:`node`: if ``IGN`` is set, the extension can be safely
ignored, but **MUST** be forwarded to the next hop if the overall
frame is forwarded.  If ``CLS`` is set, a node receiving the frame
with the extension **MUST** close the connection if it doesn't
understand the extension.  Finally, the ``HOP`` flag indicates a
hop-by-hop extension; if the frame is to be forwarded, the extension
**MUST** be dropped from the frame.

The flag bits are followed by 5 reserved bits, which **MUST** be set
to 0.  This is then followed by an 8-bit protocol number, just like
the carrier protocol.  The 16-bit "Extension Length" field indicates
the total size, in bytes, of the extension's data, including the
header.  As an example, if we assume the existence of an extension
that adds a 64-bit timestamp to a frame, the extension length field
would be set to 12: 4 bytes for the header and 8 bytes for the
timestamp.

.. _proto-negot:

Protocol Versioning and Negotiation
-----------------------------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Protocol Number
     - Since Minor
     - Sent From
     - Sent To
   * - 0
     - 0
     - Nodes; Clients
     - Nodes; Clients

The protocol version field specifies the overall major version of the
Humboldt protocol, labeling it "0".  This version designates all the
basic functionality described herein.  However, it is possible that
additional functionality will be required in the future, both
incremental additions and breaking changes.  To facilitate this, the
Humboldt protocol version consists of both a *major* and *minor*
version number; changes that break compatibility will result in an
increment of the major version number, while changes that introduce
additional optional functionality will increment the minor version
number.

The meaning of the version numbers is only one piece of the puzzle;
two Humboldt nodes must also agree on the protocol version to use
between them.  The major version number is always included in the
first 4 bits of the carrier protocol, but that doesn't constitute
agreement.  To agree, the two Humboldt nodes must *negotiate* the
major version that they will use, which requires them knowing what
versions the other accepts.  This exchange is done using a simple
rule: the first frame sent on a new conduit will always use the
highest major protocol version number supported by that node.  If both
nodes use the same major version, no additional protocol overhead is
required, as agreement has been reached.

Next, we must consider what happens if the two nodes do not use the
same major version.  Here, we can assume that there is a minimum major
version that is supported by the implementations.  If a node receives
a frame that uses a major version within the range it understands, it
simply retransmits its initial frame using that major version, and
uses that for the remainder of the lifetime of the conduit; it can
safely ignore the error message it will receive from the other node.
If, however, the frame is outside the range of versions it
understands, the node must return an error, using protocol number 0
with the ``ERR`` bit set, and using either its maximum or minimum
known protocol major version, depending on whether the received frame
has a version higher or lower than its own range.

Once the two nodes have exchanged error replies, it is now known, by
both sides, which versions, if any, are mutually supported.  If there
are no mutually supported versions, then the link must be terminated;
otherwise, the nodes pick the highest mutually supported protocol
version and retransmit their initial frames using that version.

.. note::

   The content of the protocol 0 ``ERR`` frame is always a UTF-8
   encoded string suitable for inclusion in a log or, in the case of a
   client conduit, suitable for display to a user.  It is **NOT
   RECOMMENDED** that this message be localized; these errors should
   be in English to facilitate web searches for the error message.

The minor version numbers are exchanged with the initial frame, and
serve to highlight optional features understood by the two nodes.  It
is assumed that any Humboldt node understands minor versions from 0 to
its advertised minimum version number.  In major version 0 of the
Humboldt protocol, the initial frame is described by
:ref:`node-id-proto`.

Building Blocks
===============

In this section, we describe the building blocks of the encapsulated
protocols.  This consists largely of common :term:`algorithms`,
although other common building blocks, such as encodings, may also be
described.

.. index:: ! round trip time
.. index:: ! RTT
.. _rtt-calc:

Round Trip Time
---------------

Several aspects of Humboldt's protocols depend on :abbr:`RTT (Round
Trip Time)`, an estimate of the amount of time that is required for a
reply to a protocol message to be received.  Humboldt uses an
adaptation of the Jacobson/Karels algorithm [Jacobson1988A2]_ for
round trip time estimation.  This algorithm takes the sampled RTT
:math:`m` and uses it to maintain a running average :math:`a`, also
maintaining an average deviation :math:`v`; these data together are
then used in computing a retransmission timeout (see
:ref:`retrans-ack`).  The algorithm uses a pair of scaling factors,
identified below as :math:`\delta_a` and :math:`\delta_v`.  With
:math:`r` identifying the retransmission timeout, this calculation
looks like:

.. math::

   \Delta &= m - a

   a &= a + \delta_a \Delta

   v &= v + \delta_v (|\Delta| - v)

   r &= a + 4v

For Humboldt, we pick :math:`\delta_a = 1/8` and :math:`\delta_v =
1/4`; with these choices, it is then possible to use integer
arithmetic by scaling the average RTT and variance:

.. math::

   a_{\delta} &= 8a

   v_{\delta} &= 4v

   \Delta &= m - a_{\delta} / 8

   a_{\delta} &= a_{\delta} + \Delta

   v_{\delta} &= v_{\delta} + (|\Delta| - v_{\delta} / 4)

   r &= a_{\delta} / 8 + v_{\delta}

Implementing this computation in C looks like this:

.. code:: c

   measurement -= scaled_average >> 3;
   scaled_average += measurement;
   if (measurement < 0)
       measurement = -measurement;
   measurement -= scaled_deviation >> 2;
   scaled_deviation += measurement
   retransmit_timeout = (scaled_average >> 3) + scaled_deviation;

(This code is taken from appendix A.2 of [Jacobson1988A2]_; variable
names have been altered to improve clarity.)

Humboldt measures round-trip times with millisecond resolution.

.. index:: ! retransmission
.. index:: ! acknowledgment
.. _retrans-ack:

Retransmissions and Acknowledgments
-----------------------------------

In networks where data must traverse multiple hops, there is no
guarantee that a given PDU will reach its intended destination.  The
TCP protocol uses a specialized system of acknowledgments and
retransmissions to ensure that data does arrive.  Humboldt uses a
similar system in most of its encapsulated protocols: the protocols
generally utilize the ``REP`` bit of the carrier protocol to
acknowledge receipt of a particular frame, and if the original frame
sender does not receive an acknowledgment, it will retransmit the
frame.  To ensure :term:`idempotency`, protocols will generally need
to have some way to uniquely identify the frame; how this is done
varies from protocol to protocol.

Humboldt uses :term:`exponential backoff` in its retransmission logic:
often, the cause of a lost packet is the underlying network becoming
saturated, and an aggressive retransmission strategy could worsen the
network saturation.  Humboldt starts the retransmission timer with the
current round trip estimate plus 4 times the deviation (see
:ref:`rtt-calc`), then doubles that timeout after each retransmission
(with a network maximum specified by the :ref:`ret-max` configuration
value).  After a maximum number of retransmissions (specified by
:ref:`ret-cnt`), a node **MUST** declare the link dead, for all
hop-by-hop retransmissions.

.. note::

   Implementations are free to utilize randomization in calculating
   the actual time to wait between retransmissions.  However, the
   minimum interval between retransmissions **MUST NOT** be less than
   one-half the interval calculated by doubling the previous
   calculated interval.  Moreover, it is the nominal interval that is
   doubled in each round, not the randomized interval actually used.
   Finally, randomization **MUST NOT** be used for the first
   retransmission timer.

.. index:: ! broadcast

Broadcasts
----------

Some protocols engage in a :term:`broadcast` to accomplish their task.
In its simplest form, a broadcast is simply retransmission of a frame
via all links except the one the original arrived from.  However,
without some additional logic, that simple algorithm would result in
that frame continually being retransmitted over the entire network
forever.  To prevent this, all encapsulated protocols that use
broadcasting **MUST** include some form of ID into the broadcast
frame, in order to uniquely identify it.  Upon receipt of a broadcast
frame, a :term:`cache` **MUST** be checked for the ID, and if it is
not present, the frame **MUST** be retransmitted as described before,
and the ID **MUST** be placed into the cache.

.. sidebar:: Time-To-Live Limits

   Because broadcasts are expensive, there are several strategies to
   mitigate the expense.  One that is used by :ref:`link-state-proto`
   is to modify the broadcast strategy by decrementing a :abbr:`TTL
   (Time To Live)` field on the frame each time the frame is
   forwarded; when the TTL field reaches 0, the frame is not
   forwarded.

The broadcast cache is a general term, as the implementation may
choose to use either one cache for all encapsulated protocols, or one
per protocol, depending on the requirements of the implementation.  In
either case, entries in the cache **MUST** time out and be removed
from the cache after a period of time defined by the
:ref:`bcast-cache` configuration value.

Broadcast frames **MUST** also be retransmitted and acknowledged, as
described under :ref:`retrans-ack`.  The acknowledgment **MUST** be
sent even if the frame ID is in the broadcast cache.  This ensures
that the broadcast is received by each :term:`node` in the network.

.. note::

   Broadcasts are expensive, because of how many frames are generated
   during the processing of the broadcast.  As such, if there is a way
   to avoid using a broadcast, encapsulated protocols **SHOULD** use
   the alternative.  If the use of a broadcast is required to
   implement the desired algorithm, the protocol **SHOULD** take steps
   to limit the frequency of the broadcast, including batching
   updates.  Protocols **MAY** also use other mitigation strategies,
   such as TTL semantics.

.. index:: ! gossip
.. index:: ! gossip protocols
.. _gossip-proto:

Gossip Protocols
----------------

Humboldt has a need to disseminate some information across the entire
network in a timely fashion.  If broadcasts were the only way to
accomplish this, Humboldt would not be scalable, due to the huge
number of frames that would have to be broadcast.  Enter the
:term:`gossip protocols`: protocols based on frequent, pair-wise
interactions between nodes.  In these interactions, pieces of
information are selected essentially at random from a larger
collection and exchanged with other nodes.  In this way, this
information can be disseminated across the entire network without the
overhead of a broadcast protocol.

Gossip protocols are based on frequent interactions between pairs of
nodes, and there's a random element to the interaction to ensure that
all nodes eventually learn all the information being disseminated.
Additionally, to keep memory requirements in check, the information
learned through the gossip protocol must be aged out unless and until
it is learned again from another such interaction.  Humboldt nodes do
this through a cache where the total size of the cache is constrained:
if a new item of information is added to the cache, causing the cache
size constraint to be exceeded, the least recently updated item in the
cache will be discarded.  This allows the memory footprint to be kept
small, but still allows information to traverse throughout the entire
network.

.. index:: ! encoding

Protocol Encodings
------------------

The carrier protocol and its extensions is intended to be minimal and
consistent overhead, and so is laid out using explicit bit
specifications.  All of the encapsulated protocols, however, utilize
:term:`protocol buffers` [ProtoBuf]_ to specify their binary
encoding.  Protocol buffers are efficient and fast, and the protocol
buffer compiler can emit code in a variety of different languages,
which aids in interoperability between Humboldt implementations.  In
the descriptions of protocols, protobuf *messages* will be shown to
describe the encoding of particular encapsulated protocol frames.

.. index:: ! ID; node
.. index:: ! node ID

Node ID
-------

Each node in a Humboldt network has a unique, 128-bit ID.  Note that
these IDs **SHOULD** be distributed uniformly, so a UUID will not be
acceptable.  This ID is important to the routing system, in that, if a
frame is being sent to an unknown node, it will be sent to the node
with the closest ID for forwarding or other disposition.  It is
**RECOMMENDED** that the node ID be persisted in on-disk storage,
although it is also **RECOMMENDED** that nodes generate a new node ID
on startup if one is not configured.

Nodes often need to determine the distance in the ID space between two
node IDs, or between a node ID and another 128-bit identifier.  In
computing this distance, nodes **MUST** treat the ID space as
circular; that is, the distance between the all-zeros ID and the
all-ones ID is 1.

.. index:: ! ID; generation
.. index:: ! generation ID

Generation ID
-------------

Each node in a Humboldt network also has a 32-bit *generation* ID.
This ID is paired with the node ID to uniquely identify a single
invocation of a node; that is, every time a node is started, it
generates a new generation ID that can be used to distinguish the
newly started node from its :term:`ghost`.  The generation ID **MUST**
be monotonically increasing; that is, the generation ID for a newly
started node must be numerically larger than the generation ID for any
prior instance of the node with the same node ID.  While the Humboldt
protocol does not require this, a 32-bit timestamp is an acceptable
implementation for the generation ID.

.. index:: ! ID; client
.. index:: ! client ID

Client ID
---------

Each client that connects to a Humboldt node is assigned a unique,
32-bit client ID by that node (within the scope of the single node).
This ID is used by the :term:`unicast` transport to direct messages to
a given client.

.. note::

   Some implementations may be tempted to use file descriptors or
   process IDs to identify clients.  This is **NOT RECOMMENDED**, as
   otherwise a newly started client may receive messages intended for
   a recently disconnected client.  It is **RECOMMENDED** that
   Humboldt node implementations select a random number at startup,
   then assign client IDs sequentially, starting from that random
   number.  It is also **NOT RECOMMENDED** that the initial client ID
   be selected based on timestamp.  Implementations **MAY** choose to
   store the next client ID in a persistent store, as for the node ID.

.. index:: ! ID; application
.. index:: ! application ID

Application ID
--------------

The application ID serves the same purpose in :term:`anycast`,
:term:`multicast`, and :term:`broadcast` transports that the client ID
serves in the :term:`unicast` transport.  However, the application ID
is intended to be a well-known number for the specific application(s)
utilizing Humboldt.  This number **MAY** be disseminated through the
:ref:`conf-proto`, or through an application-specific registry
operating on a well-known application ID; applications **MAY** also
choose to simply hard-code the application ID, depending on the needs
of the application.

Encapsulated Protocol Types
---------------------------

The encapsulated protocols are split into two different types: the
*support* protocols (see :ref:`support-proto`) and the *transport*
protocols (see :ref:`transport-proto`).  The support protocols provide
support for the Humboldt network and, indirectly, for the transport
protocols; that is, the support protocols are responsible for
governing and maintaining the underlying network structure and
building the routing tables that are then used by the transport
protocols to actually transport data from one Humboldt client to one
or more target clients.

Additional Algorithms
=====================

In addition to the building blocks described above, and the support
protocols described in :ref:`support-proto`, there are certain
algorithms that operate mostly independently.  These are described
below.

Self-Assembly
-------------

A Humboldt network is self-assembling.  That is, a given Humboldt node
is directed to connect to one other node, and from that it discovers
additional nodes to connect to, including those nodes with IDs closest
to its own.

.. sidebar:: Conduit Persistent Storage

   The self-assembly discussion assumes that an administrative client
   directs the Humboldt node to connect to another node.  This is
   simple for new nodes, but having to do this in the case of a node
   restart is obviously suboptimal.  Therefore, it is **RECOMMENDED**
   that Humboldt nodes store at least the ID and exposed conduit(s) of
   the node with the closest ID in persistent storage.  (It is also
   **RECOMMENDED** that other discovered nodes also be stored in that
   persistent storage.)  This will allow a restarting node to
   reconnect to the Humboldt network quickly.

The first rule of self-assembly is simple: any time a node becomes
aware of another node with an ID closer to its own than any of its
current direct links, the node **MUST** immediately initiate a
connection to that other node, regardless of any other rule described
below.  The second rule is a corollary: if a node loses the conduit
between itself and the node with the closest ID, it **MUST** initiate
a reconnection to that other node, but at most once; if the
reconnection attempt fails, a Humboldt node **MUST NOT** try again.

The remaining self-assembly rules are organized around rounds of a
fixed time duration given by :ref:`asm-freq`, with no more than one
connection (other than as described above) initiated per round.  (This
rule is relaxed if there are fewer than :ref:`asm-minconn`
connections, in which case a node must attempt to initiate as many
connections as would be required to bring the total connection count
up to this value, subject to the :ref:`asm-qlen` restriction.)  Each
initiated connection is added to a queue, from which it is only
removed if the connection completes or is failed by the underlying
network protocol.  Note that a Humboldt node **MUST NOT** allow this
queue to grow larger than :ref:`asm-qlen`, except as provided for by
the first and second self-assembly rules.

In any given round, the Humboldt node **MUST** choose a node at
random, with additional weight provided to nodes with greater hop
distances, and the greatest weight provided to nodes that the Humboldt
node as learned about only through a "gossip" interaction (see
:ref:`gossip-proto`).  There is also a probability that the Humboldt
node *won't* attempt to make any additional connection; this
probability increases as the number of connections approaches
:ref:`asm-maxconn`.

.. note::

   A given Humboldt node **MAY** have any number of connections, which
   may have been initiated for any number of reasons.  The value given
   by :ref:`asm-maxconn` is used solely to compute a probability of
   *not* initiating a new connection, and that probability **MUST
   NOT** reach 1 regardless of how many connections the node actually
   has.

Message Routing
---------------

The Humboldt transport protocols need to be able to route messages to
remote nodes, regardless of the transport system.  There are a number
of ways this can be done, but Humboldt is designed to use a hybrid
routing system: a combination of a *link state* routing strategy and a
*closest to target* routing strategy.  The latter strategy, *closest
to target*, is simple to explain: the message is routed to the node
that has an ID closer to the target node's ID.  The *link state*
routing strategy is based on link state routing protocols, such as
OSPF (:rfc:`2328` and :rfc:`5340`); in these protocols, packets
describing the state of each of a node's links are distributed to all
routing nodes (see :ref:`link-state-proto` for more on Humboldt's link
state protocol).

In Humboldt's routing strategy, a node begins by searching the routing
table (described in :ref:`link-state-algorithm`) for another node with
an ID as close as possible to that which the frame is addressed.  The
frame is then forwarded to the designated next hop.  To reduce the
chance that frames traverse a cycle in the network due to routing
table recomputation, the link state algorithm computes both a
preferred primary next hop and a secondary, next-best hop; if a frame
was received from the primary next hop, the node will instead forward
it to the next-best hop instead.

.. _link-state-algorithm:

Link State Algorithm
--------------------

The main problem with a link state protocol is that each node needs to
know about all other nodes, which can lead to a large memory footprint
in the case of a large number of nodes.  This is the reason that
Humboldt uses a hybrid routing strategy: by allowing node IDs to also
designate locations, a frame can be forwarded closer to its intended
recipient without the originating or intermediate nodes even being
aware of the existence of that recipient.  With this rule, the link
state routing packets (described in :ref:`link-state-proto`) can be
restricted to a subset of the nodes, described in this document as the
:term:`horizon` of the routing protocol.  This is accomplished by
enforcing a :term:`time to live` on the link state frame.

For more on the link state protocol, see :ref:`link-state-proto` and
:ref:`link-lost-proto`.  The remainder of this section describes the
algorithm used to construct the routing table from the link state
table, composed of the known link state frames, which are cached by
the node.

.. sidebar:: The Link State Computation Timer

   The timer controlled by :ref:`ls-compute` is intended to allow
   updates to the routing table to be *batched* together.  Without
   this feature, each link state update would immediately trigger
   another routing table recomputation, which could result in a lot of
   wasted computation.  By batching updates, the node is given time to
   absorb related link state updates without a lot of wasted
   recomputation.

Every time the link state table is updated, the node begins a timer
(controlled by the :ref:`ls-compute` configuration value).  After this
timer expires, the link state algorithm is executed on the contents of
the link state table, with additional updates not applied until the
routing table has been recomputed.  The algorithm itself is based on
the one described in the "Route Calculation" section of
[Peterson2007]_, chapter 4.2, page 281, and it uses two temporary
lists, one of which becomes the new routing table: these lists are
designated the ``Tentative`` and ``Confirmed`` lists, and they contain
entries of the form ``(Destination, Cost, NextHop)``.  In Humboldt's
version of the algorithm, the lists are allowed to contain two entries
for each ``Destination``.  The algorithm consists of 4 steps:

1. Initialize the ``Confirmed`` list with an entry for the node
   executing the algorithm; this entry has a cost of 0.

2. For the node just added to the ``Confirmed`` list in the previous
   step, call it node ``Next`` and select its link state frame.

3. For each neighbor (``Neighbor``) of ``Next``, calculate the cost
   (``Cost``) to reach this ``Neighbor`` as the sum of the cost from
   the executing node to ``Next`` and from ``Next`` to ``Neighbor``.
   Then:

   * If ``Neighbor`` is currently not on either list, add ``(Neighbor,
     Cost, NextHop)`` to ``Tentative``, with ``NextHop`` being the
     locally connected node corresponding to ``Next``.

   * If ``Neighbor`` has 1 entry on ``Confirmed`` via a different next
     hop, but no entry on ``Tentative``, add it to ``Tentative``.

   * If ``Neighbor`` has 2 entries on ``Confirmed``, skip it.

   * if ``Neighbor`` has an entry on ``Tentative`` via a different
     next hop, add it to ``Tentative``.

   * If ``Neighbor`` has an entry on ``Tentative`` via the same next
     hop, update the ``Cost`` of that entry if it is less than what we
     previously computed.

4. If ``Tentative`` is empty, stop.  Otherwise, pick the lowest cost
   ``Tentative`` entry: if there are 2 entries on ``Confirmed`` (which
   shouldn't happen), discard the entry and repeat Step 4; otherwise,
   add it to ``Confirmed`` and go to Step 2.

For Humboldt, the ``Cost`` in the link state frame is the smoothed
:abbr:`RTT (Round Trip Time)`; see :ref:`rtt-calc` for details on how
the round trip time is calculated.
