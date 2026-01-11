# Quickstart

## Bootstrap
```bash
./scripts/bootstrap.sh
```

## Validate / compile / eval
```bash
make doctor
make index
make validate
make compile
make eval
```

## Run an agent locally
```bash
./bin/cbw-agent run agents/specs/examples/hello_world.agent.yaml --input "hello" --runtime local
```
