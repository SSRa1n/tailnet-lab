#!/usr/bin/env python3

import subprocess
import time
import webbrowser
import os
from pathlib import Path

# Optional: set your docker compose directory here
COMPOSE_DIR = Path(".")

def run(cmd, capture_output=False):
    print(f"\n>>> Running: {cmd}")

    result = subprocess.run(
        cmd,
        shell=True,
        cwd=COMPOSE_DIR,
        text=True,
        capture_output=capture_output
    )

    if result.returncode != 0:
        print("ERROR:")
        print(result.stderr)
        raise SystemExit(result.returncode)

    if capture_output:
        output = result.stdout.strip()
        print(output)
        return output

    return None


def main():
    print("Starting Headscale stack...")

    # 1. docker compose --profile ui up -d
    run("docker compose --profile ui up -d")

    # Give containers a few seconds to fully boot
    input("Waiting for containers to start. Press Enter to continue...")

    # 2. Create API key
    api_key_output = run(
        "docker exec headscale headscale apikeys create",
        capture_output=True
    )

    # 3. Open browser
    print("\nOpening admin UI...")
    webbrowser.open("http://localhost:3000/admin")

    # 4. Create users
    run("docker exec headscale headscale users create namoadmin@localhost")
    run("docker exec headscale headscale users create namoworker@localhost")

    # 5. Create reusable preauth key for user 1
    user1_key = run(
        "docker compose exec headscale "
        "headscale preauthkeys create "
        "--user 1 --reusable --expiration 24h",
        capture_output=True
    )

    # 6. Create reusable preauth key for user 2
    user2_key = run(
        "docker compose exec headscale "
        "headscale preauthkeys create "
        "--user 2 --reusable --expiration 24h",
        capture_output=True
    )

    print("\n==============================")
    print("CAPTURED OUTPUTS")
    print("==============================")

    print("\nAPI KEY:")
    print(api_key_output)

    print("\nUSER 1 PREAUTH KEY:")
    print(user1_key)

    print("\nUSER 2 PREAUTH KEY:")
    print(user2_key)

    login_server = "192.168.1.102"
    if os.argv[1]:
        login_server = os.argv[1]

    # Optional: save outputs to file
    with open("headscale_keys.txt", "w") as f:
        f.write("API KEY\n")
        f.write(api_key_output + "\n\n")

        f.write("USER1 PREAUTH KEY\n")
        f.write(f"tailscale up --auth-key={user1_key} --login-server=http://{login_server}:8100" + "\n\n")

        f.write("USER2 PREAUTH KEY\n")
        f.write(f"tailscale up --auth-key={user2_key} --login-server=http://{login_server}:8100" + "\n")

    print("\nSaved outputs to headscale_keys.txt")


if __name__ == "__main__":
    main()