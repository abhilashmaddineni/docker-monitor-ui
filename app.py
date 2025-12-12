from flask import Flask, render_template
import docker
import os
from datetime import datetime

app = Flask(__name__)
client = docker.from_env()

LOG_FILE_1 = "/logs/container-monitor.log"
LOG_FILE_2 = "/logs/docker_cleanup.log"

# Read logs safely
def read_logs(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.readlines()
    return ["Log file not found."]

@app.route("/")
def dashboard():
    containers_info = []

    for c in client.containers.list(all=True):
        stats = c.attrs
        started = stats["State"].get("StartedAt", "N/A")
        status = stats["State"].get("Status", "N/A")

        containers_info.append({
            "name": c.name,
            "image": stats["Config"]["Image"],
            "status": status,
            "started": started,
            "id": c.short_id
        })
    
    return render_template("dashboard.html", containers=containers_info)

@app.route("/logs")
def logs():
    monitor_log = read_logs(LOG_FILE_1)
    cleanup_log = read_logs(LOG_FILE_2)

    return render_template("logs.html",
        monitor_log=monitor_log,
        cleanup_log=cleanup_log
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
