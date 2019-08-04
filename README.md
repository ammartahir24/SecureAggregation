# SecureAggregation

An implementation of Secure Aggregation algorithm based on "Practical Secure Aggregation for Privacy-Preserving Machine Learning
(Bonawitz et. al)" in Python.

Dependencies: Flask, socketio and socketIO_client

`pip install Flask`

`pip install socketio`

`pip install socketIO-client`

# Usage:
client side:
Init:

`c = secaggclient(host,port)`

Give weights needed to be transmitted (originally set to zero)

`c.set_weights(nd_numpyarray,dimensions_of_array)`

Set coomon base and mod

`c.configure(common_base, common_mod)`

start client side:

`c.start()`

server side:
init:

`s = secaggserver(host,port,n,k)`

where n is number of selected clients for the round and k is number of client responses required before aggregation process begins

start server side:

`s.start()`
