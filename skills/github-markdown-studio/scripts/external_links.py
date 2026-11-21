"""List external references offline. Check only explicitly selected public HTTPS pages."""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import subprocess
from urllib.parse import quote, urlsplit

from audit import Auditor


def page_url(raw):
    page = raw.partition("#")[0]
    if any(ord(c) <= 32 or ord(c) == 127 for c in page) or "\\" in page:
        return None
    try:
        uri = urlsplit(page)
        host = uri.hostname or ""
        labels = host.split(".")
        if uri.scheme != "https" or uri.netloc.lower() not in (host, host + ":443") or "?" in page:
            return None
        if len(labels) < 2 or not labels[-1][:1].isalpha():
            return None
        if not all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label) for label in labels):
            return None
        return "https://" + host + quote(uri.path or "/", safe="/!$&'()*+,;=:@%")
    except (ValueError, UnicodeError):
        return None


def inventory(root, paths):
    refs = []
    audit = Auditor(root, external_references=refs).run(paths)
    if not audit["files_checked"] or any(f["code"] in {"SCOPE", "DOCUMENT_PARSE", "UNSUPPORTED_DOCUMENT"}
                                        for f in audit["findings"]):
        raise ValueError("Select readable Markdown files or directories inside the repository")
    pages, omitted = {}, []
    for path, line, raw in refs:
        location = {"path": path, "line": line}
        page = page_url(raw)
        if page is None:
            omitted.append(location)
        else:
            if raw.partition("#")[2]:
                location["fragment_status"] = "not-run"
            pages.setdefault(page, []).append(location)
    return pages, omitted


def check(page, curl):
    host = urlsplit(page).hostname
    try:
        rows = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
        addresses = list(dict.fromkeys(ipaddress.ip_address(r[4][0]) for r in rows))
        if not addresses or any(not a.is_global or a.is_multicast or a.is_reserved for a in addresses):
            return {"status": "blocked", "reason": "public-address-required"}
        # Give curl the addresses we inspected. Keep the original hostname for TLS verification.
        pins = ",".join(f"[{a}]" if a.version == 6 else str(a) for a in addresses)
        env = {k: os.environ[k] for k in ("SystemRoot", "WINDIR") if k in os.environ}
        result = subprocess.run(
            [str(curl), "--disable", "--globoff", "--noproxy", "*", "--proto", "=https",
             "--resolve", f"{host}:443:{pins}", "--head", "--silent", "--output", os.devnull,
             "--connect-timeout", "5", "--max-time", "10", "--write-out", "%{http_code}", "--", page],
            env=env, cwd=Path(__file__).resolve().parent, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=12,
        )
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return {"status": "blocked", "reason": "transport"}
    if result.returncode or not re.fullmatch(rb"[1-5][0-9]{2}", result.stdout):
        return {"status": "blocked", "reason": "transport", "curl_exit": result.returncode}
    status = int(result.stdout)
    if 200 <= status < 300:
        outcome = "pass"
    elif status in (404, 410):
        outcome = "fail"
    else:
        outcome = "blocked"
    return {"status": outcome, "http_status": status}


def report(root, paths, selected, curl):
    pages, omitted = inventory(root, paths)
    chosen = set(selected)
    if len(chosen) > 20 or not chosen.issubset(pages):
        raise ValueError("Select up to 20 exact page URLs from the offline inventory")
    if chosen and (not curl.is_absolute() or not curl.is_file()):
        raise ValueError("Supply the absolute path to a trusted curl executable with --curl")
    results = []
    for page, locations in pages.items():
        result = check(page, curl) if page in chosen else {"status": "not-run"}
        results.append({"url": page, "locations": locations, **result})
    return {"pages": results, "omitted_locations": omitted}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("paths", nargs="+", help="Root-relative Markdown files or directories")
    parser.add_argument("--check", action="append", default=[], metavar="URL", help="Check this inventoried page")
    default = Path(os.environ.get("SystemRoot", "C:/Windows"), "System32/curl.exe") if os.name == "nt" else Path("/usr/bin/curl")
    parser.add_argument("--curl", type=Path, default=default, help="Absolute path to a trusted curl")
    args = parser.parse_args()
    try:
        result = report(args.root, args.paths, args.check, args.curl)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return int(any(p["status"] in {"blocked", "fail"} for p in result["pages"]))


if __name__ == "__main__":
    raise SystemExit(main())
