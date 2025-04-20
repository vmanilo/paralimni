## Usage

1. Use signup endpoint to get authorisation token
2. Use token for get_dividends API call


### Dev run

1.Required tools: docker, docker-compose, uv

Installation uv docs: https://docs.astral.sh/uv/getting-started/installation/#standalone-installer
```bash
  $ brew install uv
```

2.Env setup

```bash
  $ uv sync
```

3.Prepare .env file based on env.example 

With `APP_LOG_LEVEL=debug` will be enabled SQL logs as well.

4.Run in dev mode:
```bash
  $ make dev
```

5.Open http://localhost:8000/docs

### Prod run

1.Prepare .env.prod file based on env.example

2.Run in prod mode:
```bash
  $ make prod
```

3.Open http://localhost:8000/docs


### Run tests

```bash
    $ make test
```

### Run load tests

Required tool: k6

Installation docs: https://grafana.com/docs/k6/latest/set-up/install-k6/
```bash
  $ brew install k6
```

In one terminal run prod version

```bash
    $ make prod
```

From another terminal run load test

```bash
    $ make load-test
```
