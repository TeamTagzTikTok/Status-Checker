import requests
import subprocess
import time
import platform

webhook_url = "WEBHOOK_URL"
discord_user_id = "DISCORD_USER_ID"
targets = [
    "IP:PORT:PING",
    "IP:PORT:code:404",
    "IP:PORT:code:403",
]

status_cache = {}


def send_webhook(ip, status_type, method, code=None):
    title = "Server Online!" if status_type == "online" else "Server Offline!"
    color = 0x57F287 if status_type == "online" else 0xED4245
    description = (
        f"Server `{ip}` is online again ✅ <@" + discord_user_id + ">" if status_type == "online"
        else f"Server `{ip}` is offline!\nDevice has not responded to **{method}** for 5 seconds! <@" + discord_user_id + ">"
    )

    embed = {
        "title": title,
        "description": description,
        "color": color
    }

    if method == "code" and code:
        embed["fields"] = [{"name": "Expected Code", "value": str(code)}]

    requests.post(webhook_url, json={"embeds": [embed]})


def ping_host(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        subprocess.check_output(["ping", param, "1", ip], stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def check_http_code(ip, port, expected_code):
    try:
        url = f"http://{ip}:{port}"
        r = requests.get(url, timeout=3)
        return r.status_code == expected_code
    except:
        return False


def parse_target(target):
    parts = target.split(":")
    ip, port, method = parts[0], parts[1], parts[2]
    code = int(parts[3]) if len(parts) == 4 else None
    return ip, port, method, code


def monitor():
    while True:
        for target in targets:
            ip, port, method, code = parse_target(target)
            identifier = f"{ip}:{port}:{method}:{code}" if code else f"{ip}:{port}:{method}"

            is_up = False
            if method == "ping":
                is_up = ping_host(ip)
            elif method == "code":
                is_up = check_http_code(ip, port, code)

            last_status = status_cache.get(identifier)

            if last_status != is_up:
                status_cache[identifier] = is_up
                send_webhook(ip, "online" if is_up else "offline", method, code)

        time.sleep(5)


if __name__ == "__main__":
    monitor()
