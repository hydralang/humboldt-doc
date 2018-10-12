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
documentation describes version 0.  The next two bits are flag bits,
used to modify the :term:`encapsulated protocol`; in general, the
``REP`` flag indicates a reply, and ``ERR`` indicates an error
report.  The two bits following the flag bits are reserved, and
**MUST** be set to 0.

The "Protocol" field contains an 8-bit protocol number.  The protocol
number space is split into two parts: protocol numbers from 0 to 127
are assigned to encapsulated protocols, while protocol numbers from
128 through 255 are intended to identify *extensions* to the carrier
protocol.  Finally, the "Total Frame Length" field is, as the name
suggests, a 16-bit byte length which includes the frame header.

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
   mitigate the expense.  One that is used by :ref:`link-state` is to
   modify the broadcast strategy by decrementing a :abbr:`TTL (Time To
   Live)` field on the frame each time the frame is forwarded; when
   the TTL field reaches 0, the frame is not forwarded.

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
learned about through the gossip protocol must be aged out unless and
until it is learned about again from another such interaction.
Humboldt nodes do this through a cache where the total size of the
cache is constrained: if a new item of information is added to the
cache, causing the cache size constraint to be exceeded, the least
recently updated item in the cache will be discarded.  This allows the
memory footprint to be kept small, but still allows information to
traverse throughout the entire network.
