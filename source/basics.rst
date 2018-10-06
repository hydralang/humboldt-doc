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

Common Algorithms
=================

An encoding of the contents of a PDU is insufficient to describe a
protocol; a protocol specification must also describe the behavior:
cases when particular messages are sent, what to do when receiving
particular messages, and algorithms to execute with the data collected
by means of the protocol exchange.  With Humboldt, there are several
distinct encapsulated protocols, but many of them exhibit common
:term:`algorithms`.  Additionally, a given node must execute other
algorithms that, while related to particular protocols, may be
executed unrelated to the receipt of frames encapsulating that
protocol.  This section describes some of these algorithms.

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
