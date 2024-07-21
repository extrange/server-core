# Immich-specific Notes

## Update

```
docker compose pull immich-server immich-microservices immich-machine-learning immich-redis immich-database
docker compose up -d --force-recreate --remove-orphans immich-server immich-machine-learning immich-redis immich-database
```

## `immich-cli` authentication

```
docker compose exec -it immich-server bash
immich login-key http://localhost:3001/api <API-KEY>
immich upload -r <UPLOAD_DIR>
```

Obtain API key from 'Account Settings' under user icon.

## Connect to Postgresql DB

```
psql postgres://postgres:postgres@immich_postgres:5432/immich
```