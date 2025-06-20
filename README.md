# My Home Server

Containers on my home server, which are exposed to the internet or Tailscale. See my [blog] for more details.

## \*.internal.nicholaslyz.com

Sites under this hostname are routed via Tailscale (and therefore are not publicly accessible). This is done via an `A` record pointing to the Tailscale private IP of the Traefik sidecar container. They are therefore publicly resolvable, but not publicly routable.

A limitation of this is that when the Traefik sidecar container is shared to other tailnets, there is a chance that the hostname may resolve to an internal IP in that tailnet, rather than this tailnet, due to the use of a [1 to 1 NAT] which Tailscale uses to avoid IP collisions across tailnets.

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
[1 to 1 NAT]: https://tailscale.com/blog/choose-your-ip
