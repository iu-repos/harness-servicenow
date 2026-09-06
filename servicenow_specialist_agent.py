import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_INSTANCE_URL = "https://dev395848.service-now.com"


@dataclass
class ServiceNowConfig:
    instance_url: str
    username: str
    password: str


class ServiceNowClient:
    def __init__(self, config: ServiceNowConfig) -> None:
        self.config = config

    def _build_url(self, path: str, query: dict[str, str] | None = None) -> str:
        normalized = self.config.instance_url.rstrip("/")
        url = f"{normalized}/{path.lstrip('/')}"
        if query:
            return f"{url}?{urllib.parse.urlencode(query)}"
        return url

    def _headers(self) -> dict[str, str]:
        auth_raw = f"{self.config.username}:{self.config.password}".encode("utf-8")
        auth_token = base64.b64encode(auth_raw).decode("ascii")
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_token}",
        }

    def request(
        self,
        method: str,
        path: str,
        query: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url=self._build_url(path, query=query),
            data=data,
            method=method,
            headers=self._headers(),
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8")
                if not body:
                    return {}
                return json.loads(body)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"ServiceNow API error ({exc.code}): {body}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Connection error: {exc.reason}") from exc

    def ping(self) -> dict[str, Any]:
        return self.request(
            "GET",
            "/api/now/table/sys_user",
            query={"sysparm_limit": "1", "sysparm_fields": "sys_id,user_name"},
        )

    def list_records(self, table: str, limit: int) -> list[dict[str, Any]]:
        data = self.request(
            "GET",
            f"/api/now/table/{table}",
            query={"sysparm_limit": str(limit)},
        )
        results = data.get("result")
        if not isinstance(results, list):
            raise RuntimeError("Invalid API response: expected list in 'result'.")
        return results

    def create_record(self, table: str, record: dict[str, Any]) -> dict[str, Any]:
        data = self.request("POST", f"/api/now/table/{table}", payload=record)
        result = data.get("result")
        if not isinstance(result, dict):
            raise RuntimeError("Invalid API response: expected object in 'result'.")
        return result


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing environment variable '{name}'. "
            "Configure your credentials before running the agent."
        )
    return value


def load_config() -> ServiceNowConfig:
    instance_url = os.getenv("SN_INSTANCE_URL", DEFAULT_INSTANCE_URL).strip()
    username = _required_env("SN_USERNAME")
    password = _required_env("SN_PASSWORD")
    return ServiceNowConfig(instance_url=instance_url, username=username, password=password)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ServiceNow specialist agent for development and automation tasks."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("ping", help="Validate connection and credentials.")

    list_parser = subparsers.add_parser("list", help="List records from a ServiceNow table.")
    list_parser.add_argument("--table", required=True, help="Table name (example: incident).")
    list_parser.add_argument("--limit", type=int, default=5, help="Number of records to fetch.")

    create_parser = subparsers.add_parser("create", help="Create a record in a ServiceNow table.")
    create_parser.add_argument("--table", required=True, help="Table name (example: change_request).")
    create_parser.add_argument(
        "--data",
        required=True,
        help="JSON payload string for the record fields.",
    )

    return parser.parse_args()


def run() -> int:
    args = parse_args()
    config = load_config()
    client = ServiceNowClient(config)

    if args.command == "ping":
        response = client.ping()
        count = len(response.get("result", []))
        print(f"Connection successful. Retrieved {count} user record(s).")
        return 0

    if args.command == "list":
        if args.limit < 1:
            raise RuntimeError("--limit must be greater than zero.")
        records = client.list_records(args.table, args.limit)
        print(json.dumps(records, indent=2, ensure_ascii=True))
        return 0

    if args.command == "create":
        try:
            payload = json.loads(args.data)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid JSON payload for --data: {exc.msg}") from exc
        if not isinstance(payload, dict):
            raise RuntimeError("--data must be a JSON object.")
        result = client.create_record(args.table, payload)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0

    raise RuntimeError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
