# My Home Server

Containers comprising my home server. See my [blog] for more details.

- `compose.d/`: contains individual container specification files
- `services/`: individual container configuration/mounted volumes
- `nginx/`: reverse proxy configuration

Renovate config:

- Docker image digest updates are committed directly without a PR to reduce noise (they can't be grouped, as they are considered major version updates).
- Minor tag version updates are group in a single PR
- Major tag version updates are in individual PRs

## Updating Postgres containers across major versions

Move `data` to `old` and remount:

```yml
volumes:
  - ../services/metabase/old:/var/lib/postgresql/data
```

Dump database:

```sh
pg_dumpall -U $POSTGRES_USER -l $POSTGRES_DB > /var/lib/postgresql/data/dump.sql
```

Upgrade image version, then mount the `old` directory to `old`:

```yml
volumes:
  - ../services/metabase/data:/var/lib/postgresql/data
  - ../services/metabase/old:/old
```

Rebuild DB:

```sh
psql -U $POSTGRES_USER -d $POSTGRES_DB -f /old/dump.sql
```

[blog]: https://nicholaslyz.com/blog/2022/05/22/my-self-hosting-journey/
