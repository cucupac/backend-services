# Spy Listener

Listens for VAAs (messages) in Wormhole's Guardian Network via gRPC subscription to Wormhole's Guardian Spy. This Spy Listener implementation specifically listens for VAAs relevant to Ax Protocol. When a relevant VAA in the Guardian Network is received, the Spy Listener publishes the message to an [AMQP queue](rabbitmq) for the Relayer to pick up.

## Docker Commands

Refer to [docker-compose.yml](../../docker-compose.yml) for more information.

### Run a Docker Container

Make sure your .env and/or tests.env files have been created and populated with the correct information.

| Service Name | Command                           | Notes                                                                                             |
| ------------ | --------------------------------- | ------------------------------------------------------------------------------------------------- |
| db           | `sh docker-compose up -d db`      | Make sure to comment and uncomment the appropriate database URL in [env.py](./migrations/env.py). |
| test_db      | `sh docker-compose up -d test_db` | Make sure to comment and uncomment the appropriate database URL in [env.py](./migrations/env.py). |
| rabbitmq     | `docker-compose up -d rabbitmq`   | Additional setup is required if user authentication is desired.                                   |
| ...          | ...                               | ...                                                                                               |

### RabbitMQ User Setup Command Examples

More information can be found in the official [RabbitMQ docs](rabbitmq-docs).

| Action               | Command                                                                                    |
| -------------------- | ------------------------------------------------------------------------------------------ |
| List all users       | `docker-compose exec rabbitmq rabbitmqctl list_users`                                      |
| Add a new user       | `docker-compose exec rabbitmq rabbitmqctl add_user 'my_user' 'my_pa55word'`                |
| Set user permissions | `docker-compose exec rabbitmq rabbitmqctl set_permissions -p '/' 'my_user' '.*' '.*' '.*'` |
| Set user tags        | `docker-compose exec rabbitmq rabbitmqctl set_user_tags 'my_user' 'administrator'`         |
| Delete a user        | `docker-compose exec rabbitmq rabbitmqctl delete_user 'guest'`                             |

[rabbitmq-docs]: https://www.rabbitmq.com/access-control.html
