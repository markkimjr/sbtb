"""Print the FastAPI OpenAPI schema as JSON to stdout.

Consumed by `@sbtb/client`'s generate script, which pipes the output to
`openapi-typescript` to produce typed bindings for the web app.

Usage:
    uv run --directory server/ -m scripts.generate_openapi
"""

import json
import sys

from sbtb.app import app


def main() -> None:
    json.dump(app.openapi(), sys.stdout)


if __name__ == "__main__":
    main()
