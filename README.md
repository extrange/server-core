# My Home Server

Containers on my home server, which are exposed to the internet or Tailscale. See my [blog] for more details.

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
