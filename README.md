# My Home Server

Containers comprising my home server. See my [blog] for more details.

- `compose.d/`: contains individual container specification files
- `services/`: individual container configuration/mounted volumes
- `nginx/`: reverse proxy configuration

Renovate config:

- Docker image digest updates:
  - grouped
  - committed directly (no notifications)
  - note: they are treated separate from major/minor/patch updates in config
- Minor tag updates:
  - grouped
  - automerged (so I get email notifications)
- Major tag updates:
  - individual PRs
  - manually merge

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
