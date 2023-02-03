# Ax Protocol Relayer Service

This monorepo contains all code relevant to Ax Protocol's Cross-Chain Relayer Service.

Currently, Wormhole is the only protocol that is supported by this service, but support for other cross-chain messaging protocols will be added as necessary.

# TODO
**ax-relayer**
- [ ] Restructure monorepo such for proper management of CI/CD pipeline, environment varibles, database migrations, etc.
- [X] Figure out how to properly close AMQP connection -> connection.close().
- [ ] Figure out why we can't stop server via CTRL+C KeyboardInterrupt (likely ralated to AMQP connection).

**ax-relayer/wormhole/spy_listener**
- [ ] Design and implement message reliability scheme.
  - [channel] publisher_confirms=True
  - [message] delivery_mode=DeliveryMode.PERSISTENT
  - [publish] mandatory=True
  - Handle message republishing based on return object of exchange.publish()
- [ ] Finish unit tests
- [ ] Integration tests

**ax-relayer/wormhole/relayer**
- [ ] Design and implement message reliability scheme.
  - [queue] durable=True
  - [incoming message] message.ack()
- [ ] Finish unit tests
- [ ] Integration tests
