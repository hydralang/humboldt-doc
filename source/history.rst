===========================
A Brief History of Humboldt
===========================

.. note::

   This document is meant to, in the language of Internet standards,
   be informative, not normative.  That is, none of the contents of
   this document are intended to describe Humboldt, only to inform the
   reader of where some elements of the design may have originated.

In the beginning, there was :abbr:`IRC (Internet Relay Chat)`.  In
multiple server IRC, the servers are connected together with an
overlay network; however, owing to the way messages are sent between
servers, the network must be a :abbr:`DAG (Directed Acyclic Graph)`, a
technical term for a network where there is exactly one path between
any two nodes, and thus no circular paths.  As a consequence, if one
of the links breaks, the network segments into two separate networks,
resulting in a large amount of traffic as the network processes the
disconnection and subsequent reconnection.  This also disrupts
communication between users of the network, as some messages may not
be delivered.

As an IRC developer, having a new underlying overlay network to
address these problems and enable redundant links has been something
of a holy grail.  I have been thinking about the problem for years,
even as I learned about all sorts of networking technologies, such as
:term:`link-state routing protocols`, :term:`distributed hash tables`,
and other technologies.  However, creation of a full-featured overlay
network is a complex task, and I've made several false starts at it
over the years.

Eventually, I accepted the suggestion by another IRC developer to
separate the overlay network component from the server
implementation.  (This suggestion was advanced prior to the hype of
the microservices architecture, and before I personally had experience
working with microservices.)  I also came up with additional use cases
for an overlay network.  I started referring to the concept as
"Humboldt", as I viewed it as sort of a tangle of tentacles
everywhere, evoking the image of a squid; this is the inspiration for
the name.

Humboldt itself is based on the concept of layered protocols, like the
OSI model: each protocol layer builds on the one underneath it and
provides additional services that can be leveraged by the layer above
it; additional protocols operating alongside the main protocols
provide additional functionality, like establishing routing.
Additionally, to achieve scalability, it is important that no one node
need know the entire state of the network; this influenced the hybrid
routing strategy.  At the same time, nodes with neighboring IDs must
be able to connect with each other, to accommodate the :term:`DHT`
routing; this resulted in the adoption of :term:`gossip protocols` for
disseminating distant node information.

The final result of this decades-long exploration and learning about
networking protocols is the design found here.  The state machine is
kept simple; the use of two routing protocols keeps the node memory
footprint small, enabling scalability; and the self-assembling
property implies a high degree of connection redundancy, reducing the
possibility that the network will segment in the same way as the
classic IRC overlay network.  Further, the fact that Humboldt is
self-contained means that the overlay network can be used in a variety
of applications, depending on need.  It can be used to coordinate a
distributed application in a single data center, but it could also be
used to allow that same distributed application to reach across the
entire Internet, enabling unprecedented disaster recovery for
applications that can be built upon its basic services.
