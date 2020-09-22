#!/usr/bin/env python3

import requests
import yaml
import argparse
import tempfile
import hashlib
import re

OUTPUT_FILENAME = "../conandata.yml"
ENDPOINT = "https://api.github.com/repos/emscripten-core/emscripten/tags"
RELEASE_REGEXP = r"(\d+\.){2}\d+"


def main(args):
    urlifier = lambda x: "https://github.com/emscripten-core/emsdk/archive/{}.tar.gz".format(
        x["name"]
    )
    output = yaml.dump(
        {
            "sources": {
                d["name"]: {
                    "sha256": hashlib.sha256(
                        requests.get(urlifier(d), stream=True).raw.read()
                    ).hexdigest(),
                    "url": urlifier(d),
                }
                for d in filter(
                    lambda x: re.match(RELEASE_REGEXP, x["name"]),
                    requests.get(ENDPOINT).json(),
                )
            }
        }, indent=4
    )
    if args.dry_run:
        print(output)
    else:
        with open(OUTPUT_FILENAME, "w") as f:
            f.write(output)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="generate conandata.yml")
    p.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="dry run, don't actually write yaml.",
    )
    main(p.parse_args())
