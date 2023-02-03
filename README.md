# Ax Relayer

This monorepo contains all code relevant to the Ax Relayer Service.

Currently, Wormhole is the only protocol supported by this service, but support for other cross-chain messaging protocols will be added as necessary.

# TODO

**ax-relayer**

-   [ ] Restructure monorepo such for proper management of CI/CD pipeline, environment varibles, database migrations, Make files, etc.
-   [ ] Fix inability to stop server via CTRL+C KeyboardInterrupt (likely ralated to AMQP connection).
-   [ ] Get clear on all possible system failures and mitigate accordingly.
-   [ ] Come up with deployment strategy.
-   [ ] Integration tests (use test_rabbitmq).

**ax-relayer/wormhole/spy_listener**

-   [ ] Fix broken unit tests.

**ax-relayer/wormhole/relayer**

-   [ ] Research websocket and architect integration into the relayer, such that the Ax frontend can hook up to the websocket.
-   [ ] Finish unit tests
    -   [ ] [Queue] Mock incoming messages
    -   [ ] [Repo] Test ability to update a row correctly (requires initial db insertion)
    -   [ ] [VAA Delivery] Success: using mocks, ensure that the row in the database gets updated to success and has transaction_hash (requires initial db insertion)
    -   [ ] [VAA Delivery] EVM client failure: using mocks, ensure that database does not have transaction_hash and that it’s status was updated to FAILED (requires initial db insertion)
