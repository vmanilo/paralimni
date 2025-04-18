# Development

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

4.Run in dev mode:
```bash
  $ make dev
```

5.Open http://localhost:8000/docs

# Prod setup

1.Prepare .env.prod file based on env.example

2.Run in prod mode:
```bash
  $ make prod
```

3.Open http://localhost:8000/docs


# Run tests

```bash
    $ make test
```