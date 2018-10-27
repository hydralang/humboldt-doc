===================
High Level Overview
===================

.. index::
   single: security layer
   single: conduit

Humboldt assumes that all nodes on its network can be trusted.
(Services that need a different trust model can implement this on top
of Humboldt.)  As such, :term:`authentication`, :term:`authorization`,
:term:`message integrity`, and :term:`message confidentiality` are
isolated into a :term:`security layer`.  Security layers are simply
abstractions that present either a :term:`stream-oriented interface`
or :term:`packet-oriented interface` to the core Humboldt protocol
processor.

The stream-oriented or packet-oriented interface used by the core
Humboldt protocol processor is referred to as a :term:`conduit`.  Each
end of a conduit is identified by a :term:`conduit URI`, which
describes the underlying network transport, the security layer, and
the network location.  A given conduit is identified by a pair of
conduit URIs.

.. index:: ! conduit; URI

Conduit URI
===========

It must be possible for a Humboldt node to describe to peers how to
connect to it.  The underlying network transport, any security layer
applied to that transport, and the network location must all be
described.  As such, the URI, described by :rfc:`3986`, makes the
perfect tool for describing one end of a conduit; the *scheme* can
identify the underlying network transport and security layer, and the
*authority* (specifically, the *host* and *port* of the authority) can
indicate the network location of the node for most transports.  (The
local transports can use the *path* of the URI, rather than the host
and port elements of the authority.)

The scheme portion of the conduit URI makes use of the "+" character
as a separator, to indicate the security layer.  For instance, if the
scheme is ``tcp``, that could indicate a stream-oriented conduit with
no security layer, while ``tcp+tls`` could be used to indicate a
stream-oriented conduit with a security layer based on TLS.  Further,
connection-specific options could be specified with the *query* of the
URI.

.. warning::

   Conduit URIs are advertised to *all* Humboldt nodes.  As such, they
   **MUST NOT** contain any security-sensitive data.  Thus, the
   *userinfo* component **MUST NOT** occur in the URI.  Further,
   usernames or passwords **MUST NOT** appear in the query.  It is
   assumed that all security-related credentials, such as usernames,
   passwords, or keys, will be contained in the node's local
   configuration.

Conduit URIs must stand alone; that is, they must contain all the
information necessary for another node to initiate a connection.  As
such, the host and port portions of the URI are expected to be
numerical.  Nodes **MUST NOT** attempt to resolve DNS addresses that
appear in the URI.

.. index:: ! conduit; URI; extended

Extended Conduit URI
--------------------

While Humboldt nodes will not resolve DNS addresses that appear in a
conduit URI, those names are convenient for humans to use.  Thus, they
**MAY** appear in an :term:`extended conduit URI`, as utilized by
Humboldt clients.  Further, it may be convenient if some
:term:`discovery` mechanism can be specified through the conduit URI.
For instance, in some organizations, DNS SRV records may provide the
information to identify a subset of Humboldt nodes.  To facilitate
this, in an extended conduit URI, the discovery mechanism **MAY** be
specified as part of the scheme, separated from it by a ".".

.. list-table::
   :header-rows: 1
   :widths: auto

   * - URI
     - Type
     - Meaning
   * - ``tcp://10.2.25.15:1824``
     -
     - TCP transport, no security layer, located at 10.2.25.15 port
       1824
   * - ``tcp+tls://10.2.25.15:1824``
     -
     - TCP transport, TLS security layer, located at 10.2.25.15 port
       1824
   * - ``local:///var/run/humboldt``
     -
     - Local stream socket, no security layer, located at
       ``/var/run/humboldt``
   * - ``udp+dtls://humboldt.example.com:1824``
     - Extended
     - UDP transport, DTLS security layer, use DNS resolution of host
       humboldt.example.com and port 1824
   * - ``tcp+gssapi.srv://example.com``
     - Extended
     - TCP transport, GSSAPI security layer, use the "srv" discovery
       scheme with host example.com

.. index:: ! conduit; advertisement

Conduit URI Advertisements
--------------------------

When conduit URIs are advertised to other peers, they may be
optionally associated with a :term:`network name`.  This mechanism is
intended to allow conduits between Humboldt nodes to make use of
localized network addresses that may not be routed through the public
Internet.  For instance, in a network where two (or more) nodes happen
to be located on machines behind a router employing IPv4 :abbr:`NAT
(Network Address Translation)`, those nodes may advertise conduit URIs
with a network name unique to the subnet that they share, and they may
connect to their neighbors using those URIs.  For any given Humboldt
node, when it attempts to connect to another, it will first attempt to
use common named networks, falling back on the conduit URIs with no
network name (which are interpreted to be public addresses) if there
are no common networks or if connections via the other URIs failed.

.. index:: ! security layer

Security Layer
==============

The security layer is solely responsible for authentication,
authorization, message integrity, and message confidentiality; as a
result, the Humboldt node doesn't need to handle (or even know about)
any of these elements of communication, vastly simplifying the
Humboldt connection state machine.  Since the security layer is
specified as part of conduit URIs, this allows a Humboldt network to
function with any combination of security layers, allowing an old
security layer to be phased out for a new one with little more than a
change of advertised conduit URIs.

.. caution::

   Because security is designed as an add-on to the Humboldt protocol
   in this fashion, Humboldt nodes may not warn administrators about
   insecure configurations.  Care must be taken to ensure that a
   Humboldt node is configured securely.

.. sidebar:: Security Layer Information

   The security layer information, including the encryption strength
   estimate, is exposed to administrative clients, and may be used for
   auditing purposes.  The encryption strength estimate is an 8-bit
   unsigned integer, intended to convey the number of bits of a
   symmetric key used to perform the encryption; if the algorithm used
   is not a symmetric key algorithm, this value should indicate the
   number of key bits of an equivalent symmetric key algorithm.

A security layer wraps the underlying network transport (e.g., TCP) in
some fashion, then presents an interface to the Humboldt protocol
processor of the same form as would be presented by that underlying
network transport.  That is, a security layer wrapping TCP would
present a stream-oriented interface, while a security layer wrapping
UDP would present a packet-oriented interface.  A security layer
**MUST** also present certain information to the protocol processor:
it **MUST** indicate whether the established conduit represents a
client or a peer; if it's a client, the security layer **MUST** also
indicate whether the client has administrative privileges; and it
**MUST** also indicate whether message integrity protections are
provided by the security layer, as well as whether message
confidentiality (encryption) is enabled and an estimate of the
strength of the encryption.  Finally, the security layer **MUST**
present, if known, the :term:`principal` that is connected via the
conduit.

.. note::

   It is possible to layer security layers on top of other security
   layers.  However, not all combinations are guaranteed to function.
   The use of multiple security layers is **NOT RECOMMENDED**.

.. important::

   To prevent reflection attacks utilizing Humboldt, nodes **MUST
   NOT** accept any Humboldt protocol frames not associated with a
   currently active and secured conduit.
