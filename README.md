# Ax Relayer

This monorepo contains all code relevant to the Ax Relayer Service.

Currently, Wormhole is the only protocol supported by this service, but support for other cross-chain messaging protocols will be added as necessary.

# TODO

**ax-relayer**

-   [ ] Restructure monorepo such for proper management of CI/CD pipeline, environment varibles, database migrations, Make files, etc.
-   [ ] Fix inability to stop server via CTRL+C KeyboardInterrupt (likely ralated to AMQP connection).
-   [ ] Get clear on all possible system failures and mitigate accordingly.
-   [ ] Come up with deployment strategy.
-   [ ] Integration tests (use test_rabbitmq and test_db docker containers).

**ax-relayer/wormhole/spy_listener**

-   [x] Finish unit tests

**ax-relayer/wormhole/relayer**

-   [x] Finish unit tests
-   [ ] Integrate websocket into the relayer
-   [ ] Test that the Ax frontend can hook up to the websocket.
