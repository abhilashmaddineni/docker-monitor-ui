from flask import Flask, render_template, redirect
import docker
from datetime import datetime, timedelta, timezone
import subprocess

app = Flask(__name__)
client = docker.from_env()

IST = timezone(timedelta(hours=5, minutes=30))


def to_ist(utc_time_str):
    """Convert UTC time from Docker to IST."""
    try:
        if not utc_time_str:
            return "N/A"
        utc = datetime.strptime(utc_time_str.split(".")[0], "%Y-%m-%dT%H:%M:%SZ")
        utc = utc.replace(tzinfo=timezone.utc)
        ist = utc.astimezone(IST)
        return ist.strftime("%Y-%m-%d %H:%M:%S IST")
    except:
        return utc_time_str


@app.route("/")
def dashboard():
    containers_info = []

    for c in client.containers.list(all=True):
        attrs = c.attrs

        containers_info.append({
            "id": c.short_id,
            "name": c.name,
            "image": attrs["Config"]["Image"],
            "command": " ".join(attrs["Config"]["Cmd"]) if attrs["Config"]["Cmd"] else "",
            "created": to_ist(attrs["Created"]),
            "started": to_ist(attrs["State"].get("StartedAt")),
            "status": attrs["State"]["Status"],
            "ports": attrs["NetworkSettings"]["Ports"],
            "restart_count": attrs.get("RestartCount", 0)
        })

    return render_template("dashboard.html", containers=containers_info)


@app.route("/logs")
def logs():
    log1 = "/var/log/container-monitor.log"
    log2 = "/var/log/docker_cleanup.log"

    def read_file(path):
        try:
            with open(path, "r") as f:
                return f.read()
        except:
            return f"Cannot read {path}"

    return render_template("logs.html",
                           monitor_logs=read_file(log1),
                           cleanup_logs=read_file(log2))


@app.route("/action/run-cleanup")
def run_cleanup():
    subprocess.call(["/bin/bash", "/scripts/docker_system_cleanup.sh"])
    return redirect("/")


@app.route("/action/recover")
def recover():
    subprocess.call(["systemctl", "restart", "docker"])
    subprocess.call(["docker", "system", "prune", "-af"])

    subprocess.call(["docker", "compose", "-f", "/root/redis-server/docker-compose.yml", "up", "-d"])
    subprocess.call(["docker", "compose", "-f", "/root/grafana/docker-compose.yml", "up", "-d"])
    subprocess.call(["docker", "compose", "-f", "/root/monitor/docker-compose.yml", "up", "-d"])

    return redirect("/")
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
