# Tailscale + Headscale Stack with Prometheus Monitoring

Instant noodle of a control-plane stack for a Tailnet using Headscale. Which includes:

- Headscale (control plane)
- Optional Headplane web UI
- Prometheus configured to scrape Headscale control-plane metrics

## Layout
```
docker-compose.yaml      # 100% AI-Generated, I have no idea how it works
config/config.yaml       # Headscale server config (set server address)
config/acls.hujson       # ACLs and user-subnet mappings
config/headplane.yaml    # Headplane UI settings (optional)
config/prometheus.yml    # Prometheus scrape config
```

## Quick start (5 minutes)

1. Edit `config/config.yaml` and edit `server_url` with the address
   your clients will use to reach Headscale.
2. Edit `config/acls.hujson` to define user and their groups/policy.
3. Edit `config/headplane.yaml` and replace `cookie_secret` with a random 32
   character value.

Generate a cookie secret with:

```bash
openssl rand -hex 16
```

## Running

From inside the folder:

```bash
docker compose up -d
```

5. (Optional) Run with headplane UI:

```bash
docker compose --profile ui up -d
```

## Create Headscale users (examples)

Create users from the host that runs the compose stack:

```bash
docker compose exec headscale headscale users create USERNAME
```

Get user IDs (for preauth keys):

```bash
docker compose exec headscale headscale users list
```

## Issue pre-auth (login) keys

Create a reusable key for a user (replace USER_ID):

```bash
docker compose exec headscale headscale preauthkeys create \
   --user USER_ID \
   --reusable \
   --expiration 24h
```

On a client, use the printed key to join the tailnet:

```bash
tailscale up --auth-key=hskey-... --login-server=http://YOUR_SERVER_IP:8100
```

## Subnet access model

The sample ACL file gives:

- `worker` access to `192.168.10.0/24`
- `cleaner` access to `192.168.20.0/24`
- `admins` unrestricted access

If you add a subnet router, tag it with `tag:subnet-router` and approve the
route in Headscale. This is for creating a gateway for a subnet without having the device inside that subnet to install tailscale

Helpful checks:

```bash
docker compose exec headscale headscale users list
docker compose exec headscale headscale routes list
```

## Headplane UI

Headplane UI is available at:

```
http://localhost:3000/admin
```

Create an API key from Headscale for `root_api_key` if you want the UI to
remain signed in:

```bash
docker compose exec headscale headscale apikeys create
```

Copy the API key value into `config/headplane.yaml` as `root_api_key`.

## Metrics (Prometheus)

This stack exposes Headscale metrics and configures Prometheus to scrape them.
- Headscale metrics are exposed in-container at `:9090` and mapped to
   `http://localhost:19090/metrics` on the host.
- Prometheus UI (container) is available at `http://localhost:9091`.

  ### Some AI-Generated metrics that look interesting
Useful metrics: connected node counts, registrations, request/error rates.
These are control-plane metrics only; to monitor host CPU/memory add a node
exporter on the hosts.

## Client-side monitoring via Tailscale web interface

1. Enable the Tailscale web client on each node:

```bash
sudo tailscale set --webclient=true
```

2. Expose the read-only web client on the network (adjust ACLs accordingly):

```bash
tailscale web --readonly --listen 0.0.0.0:5252
```

Note: Ensure your tailnet ACLs permit Prometheus to scrape those ports.

# AI-Generated Pro Tips
## Troubleshooting & tips

- If clients can't reach Headscale, verify `config/config.yaml` `server_url` is
   reachable from the client network.
- Use `docker compose logs headscale` to inspect Headscale logs.
- Use `docker compose exec headscale headscale` subcommands to inspect state.

## File layout (quick reference)

```
docker-compose.yaml
config/
   ├─ config.yaml
   ├─ acls.hujson
   ├─ headplane.yaml
   └─ prometheus.yml
```
