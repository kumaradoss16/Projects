import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from flask import (
    Flask, render_template, request, jsonify,
    Response, g
)
import nmap

app = Flask(__name__)

DB_PATH = Path("scan_history.db")


# ---------- DB Helpers (SQLite) ----------

def get_db():
    """
    Get a SQLite connection for the current request.
    Based on Flask's SQLite pattern.[web:64]
    """
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    """
    Create the scans table if it does not exist.[web:62]
    """
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS scans (
            id TEXT PRIMARY KEY,
            target TEXT NOT NULL,
            ports TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            result_json TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


# ---------- Nmap Logic ----------

def run_nmap_scan(target, ports="1-1024", arguments="-sV"):
    nm = nmap.PortScanner(nmap_search_path=(r"C:\Program Files (x86)\Nmap\nmap.exe",))
    nm.scan(hosts=target, ports=ports, arguments=arguments)

    scan_results = []

    for host in nm.all_hosts():
        host_state = nm[host].state()
        hostname = nm[host].hostname()
        for proto in nm[host].all_protocols():
            for port in sorted(nm[host][proto].keys()):
                pd = nm[host][proto][port]
                scan_results.append({
                    "host": host,
                    "hostname": hostname or "",
                    "state": host_state,
                    "protocol": proto,
                    "port": port,
                    "port_state": pd.get("state", ""),
                    "service": pd.get("name", ""),
                    "product": pd.get("product", ""),
                    "version": pd.get("version", "")
                })

    return scan_results


# ---------- Routes ----------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scan", methods=["POST"])
def api_scan():
    data = request.get_json() or {}
    target = (data.get("target") or "").strip()
    ports = (data.get("ports") or "").strip() or "1-1024"

    if not target:
        return jsonify({"error": "Target is required."}), 400

    try:
        results = run_nmap_scan(target, ports=ports, arguments="-sV")
    except nmap.PortScannerError as e:
        return jsonify({"error": f"Nmap error: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500

    timestamp = datetime.utcnow().isoformat() + "Z"
    meta = {"target": target, "ports": ports, "timestamp": timestamp}
    payload = {"meta": meta, "results": results}

    # Persist to SQLite
    scan_id = uuid.uuid4().hex
    db = get_db()
    db.execute(
        "INSERT INTO scans (id, target, ports, timestamp, result_json) VALUES (?, ?, ?, ?, ?)",
        (scan_id, target, ports, timestamp, json.dumps(payload)),
    )
    db.commit()

    return jsonify({
        "scan_id": scan_id,
        "target": target,
        "ports": ports,
        "timestamp": timestamp,
        "count": len(results),
        "results": results
    })

@app.route("/api/download/<scan_id>.<fmt>", methods=["GET"])
def api_download(scan_id, fmt):
    db = get_db()
    row = db.execute(
        "SELECT result_json FROM scans WHERE id = ?",
        (scan_id,),
    ).fetchone()

    if not row:
        return jsonify({"error": "Invalid or expired scan_id."}), 404
    
    payload = json.loads(row["result_json"])
    meta = payload["meta"]
    results = payload["results"]

    if fmt == "json":
        resp = Response(
            json.dumps(payload, indent=2),
            mimetype="application/json"
        )
        filename = f"scan_{scan_id}.json"
        resp.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return resp
    elif fmt == "csv":
        if not results:
            return jsonify({"error": "No data for this scan."}), 400
        
        import io, csv
        output = io.StringIO()
        fieldnames = ["host", "hostname", "state", "protocol", "port", "port_state", "service", "product", "version"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

        csv_data = output.getvalue()
        resp = Response(csv_data, mimetype="text/csv")
        filename = f"scan_{scan_id}.csv"
        resp.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return resp
    else:
        return jsonify({"error": "Unsupported format. Use csv or json."}), 400

@app.route("/history")
def history():
    """
    Simple scan history page: lists previous scans with links.
    """
    db = get_db()
    rows = db.execute(
         "SELECT id, target, ports, timestamp FROM scans ORDER BY timestamp DESC"
    ).fetchall()

    scans = [
         {
             "id": r["id"],
             "target": r["target"],
             "ports": r["ports"],
             "timestamp": r["timestamp"]
         }
         for r in rows
    ]

    return render_template("history.html", scans=scans)


if __name__ == "__main__":
    if not DB_PATH.exists():
        init_db()
    else:
        init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)