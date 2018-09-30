========
Glossary
========

.. glossary::

   anycast
       A transport protocol characterized by messages traveling from
       one source to one of a set of destinations, typically the
       closest destination (in terms of network distance).

   authentication
       The process of proving the identity of an entity.

   authorization
       The process of determining what activities an entity with a
       given identity may perform.

   broadcast
       A transport protocol characterized by messages traveling from
       one source to all nodes.

   conduit
       An abstraction identifying a connection (not necessarily
       stream-oriented) through an underlying network, possibly
       wrapped in a security layer.  A conduit is identified by an
       unordered pair of network addresses, representing each end of
       the connection.

   conduit URI
       A URI identifying one end of a conduit.

   discovery
       A process whereby information about a peer is obtained,
       enabling connection to that peer.

   extended conduit URI
       A conduit URI that may contain DNS names and an indication of a
       discovery mechanism.  These may be used by administrative
       clients to discover peers which a node will then be directed to
       connect to.

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

   security layer
       An abstraction in Humboldt that allows security-related
       operations to be performed in isolation from the actual
       implementation of the Humboldt family of protocols.

   stream-oriented interface
       An interface to an underlying network protocol, or to a
       security layer implemented on top of an underlying network
       protocol, that presents to the application the appearance of a
       never ending stream of data.

   unicast
       A transport protocol characterized by messages traveling from
       one source to one destination.
