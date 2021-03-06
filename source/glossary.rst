========
Glossary
========

.. glossary::

   algorithm
   algorithms
      A set of instructions for performing a computation or other work
      related to the function of a :term:`node`.

   anycast
       A transport protocol characterized by messages traveling from
       one source to the closest (in terms of network distance) of a
       set of destinations.  Typically used for interchangable
       services.

   authentication
       The process of proving the identity of an entity.

   authorization
       The process of determining what activities an entity with a
       given identity may perform.

   broadcast
       A transport protocol characterized by messages traveling from
       one source to all nodes.

   cache
       A temporary container for data.  Caches always have some
       criteria for the removal of data, and should never be the
       primary store for a piece of data.  Caches are often used for
       storage of expensive to obtain data, or for the storage of data
       that only needs to be held for a short period of time.

   carrier protocol
       A protocol intended to carry another protocol.

   conduit
       An abstraction identifying a connection (not necessarily
       stream-oriented) through an underlying network, possibly
       wrapped in a security layer.  A conduit is identified by an
       unordered pair of network addresses, representing each end of
       the connection.

   conduit URI
       A URI identifying one end of a conduit.

   debouncing
       A technique of delaying the processing of an event in order to
       batch multiple of those events together.  The name originally
       comes from electronic hardware, where a single push of a button
       could result in several electronic signals due to physical
       "bouncing" of the switch during activation; debouncing
       eliminates the duplicate signals.

   discovery
       A process whereby information about a peer is obtained,
       enabling connection to that peer.

   distributed hash tables
   DHT
       A method of splitting up data across nodes, based on a
       *consistent hash* (a hash function which does not depend on the
       number of buckets).  DHT systems often employ routing
       strategies that send messages to the nodes with an address as
       close as possible to the address implied by the data.

   encapsulated protocol
       A protocol encapsulated by another protocol.  In the case of
       Humboldt, the outer protocol is the :term:`carrier protocol`,
       and all other described protocols are encapsulated protocols.

   exponential backoff
       A retransmission technique where each subsequent retransmission
       timeout is double the timeout before.  Often, exponential
       backoff systems also incorporate an element of randomness, so
       the backoff may be within some range; they also often have an
       upper limit on the maximum time between retransmissions.

   extended conduit URI
       A conduit URI that may contain DNS names and an indication of a
       discovery mechanism.  These may be used by administrative
       clients to discover peers which a node will then be directed to
       connect to.

   extensions
       Additional data associated with a :term:`PDU` that extend how a
       :term:`node` may interpret the PDU.  For example, an extension
       may indicate that a PDU is actually only a piece of another PDU
       that is too large to be transferred through the link between
       :term:`peer` nodes.

   frame
       A discrete collection of bytes.

   ghost
       A node link that no longer exists due to a node shutdown, but
       where the Humboldt network has not yet discovered that
       condition.

   gossip protocol
   gossip protocols
       Protocols based on frequent, pair-wise interaction between
       nodes in order to disseminate information across the network.

   horizon
       A limit to the number of hops which a link state frame may
       traverse away from its originating node.

   idempotency
       A property of a protocol where the consequences of receiving a
       given frame multiple times are identical to the case where the
       frame was received exactly once.

   jitter
       The introduction of randomness into sleep times used with
       :term:`exponential backoff` in order to smooth out the
       clustering of retransmissions.

   link-state routing protocols
       Routing protocols where the nodes periodically send out
       messages to all nodes about their own state, including
       currently active links.  They are opposed to distance-vector
       routing protocols, where nodes advertise all other nodes they
       can see, but only to their immediate neighbors.

   message confidentiality
   encryption
       A cryptographic scheme used to obscure the contents of a given
       message during transport through a (potentially hostile)
       network connection.

   message integrity
       A cryptographic scheme used to prove that a given message has
       not been altered during transport through a (potentially
       hostile) network connection.

   multicast
       A transport protocol characterized by messages traveling from
       one source to a number of destinations that have subscribed to
       a group.

   network name
       An arbitrary name assigned to a network with conduit URIs with
       private addresses unreachable from the Internet.  Peers that
       have conduit URIs for the same network name are assumed to be
       able to connect to each other using those private addresses.

   node
       A Humboldt instance.

   overlay network
       A network composed of connections between entities in an
       underlying network.  The connections are said to overlay the
       underlying network (typically the Internet).

   packet-oriented interface
       An interface to an underlying network protocol, or to a
       security layer implemented on top of an underlying network
       protocol, that presents to the application the appearance of a
       sequence of (possibly but not necessarily ordered) packets of
       data.

   peer
       A node in the same network as the node being discussed.

   principal
       An identity established via cryptographic means.  For instance,
       the principal of the server in a TLS connection would be the
       distinguished name of the server's TLS certificate, while the
       principal of a client connected via a local socket would be the
       username the client is running as on the local system.

   protocol buffers
   protobuf
       A binary encoding specification that produces compact
       encodings.  The encoding is specified by a text file, which can
       be turned into source code for encoding and decoding messages
       through the use of the protocol buffer compiler, ``protoc``.

   protocol data unit
   PDU
       The fundamental unit of data in a protocol.  See
       :term:`frame`.

   rumor
   rumors
       A piece of data exchanged by a :term:`gossip protocol`.

   security layer
       An abstraction in Humboldt that allows security-related
       operations to be performed in isolation from the actual
       implementation of the Humboldt family of protocols.

   stream-oriented interface
       An interface to an underlying network protocol, or to a
       security layer implemented on top of an underlying network
       protocol, that presents to the application the appearance of a
       never ending stream of data.

   targetcast
       A transport protocol characterized by messages traveling from
       one source to the closest to a target (in terms of network
       distance) of a set of destinations.  Typically used for
       segmented services, such as distributed hash tables.

   time to live
   TTL
       A limit to the number of hops a frame may traverse.  Typically,
       this is a field in the protocol frame that is decremented prior
       to forwarding the frame; if the field is decremented to 0, the
       frame is not forwarded.

   unicast
       A transport protocol characterized by messages traveling from
       one source to one destination.
