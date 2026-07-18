import argparse
import base64
import datetime
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
from argparse import ArgumentParser
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, NotRequired, TypeAlias, TypedDict

import yaml

CMD_INFO="""
zeitwaage performs interoperability tests against known NTP version 5 implementations.
"""


class Result(TypedDict):
    client: str
    client_log: str
    pcap: str
    result: str
    server: str
    server_log: str


class TemplatableResults(Result):
    packets: list[str]


class Implementation(TypedDict):
    enabled: bool
    client: bool
    server: bool
    regex_success: NotRequired[str]
    regex_failure: NotRequired[str]


Implementations: TypeAlias = dict[str, Implementation]


class Permutation(TypedDict):
    client: str
    server: str
    regex_success: str | None
    regex_failure: str | None

logger = logging.getLogger('zeitwaage')


def main() -> None:
    parser = ArgumentParser(description=CMD_INFO)

    parser.add_argument(
        "--impls",
        type=argparse.FileType("r"),    
        default="implementations/implementations.yml",
        help="Path to the implementations YAML file",
    )
    parser.add_argument(
        "--output-dir", default="results/", help="Base directory to write data out to"
    )
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        help="Don't make any system calls, just print",
    )
    parser.add_argument(
        "--container",
        type=str,
        default="/usr/local/bin/docker",
        help="Path to docker or your preferred container manager",
    )
    parser.add_argument(
        "--perm-config",
        type=str,
        default="etc/permutation.yml",
        help="Path to the permutation configuration",
    )
    parser.add_argument(
        "--template",
        default="etc/template_results.html",
        help="Path to the HTML template for reporting",
    )
    parser.add_argument(
        "--timeout", default=10, help="Timeout in seconds for each permutation run"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker threads for permutations. You can usually set this to the number of CPU cores you have.",
    )
    parser.add_argument(
        "--verbose", action=argparse.BooleanOptionalAction, help="Enable more verbosity"
    )
    
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    try:
        args.impls = yaml.safe_load(args.impls.read())
    except yaml.YAMLError:
        logger.critical("Implementations YAML appears bad, exiting...")
        sys.exit(1)

    # Generate all the permutations of client and servers
    implementations: Implementations = args.impls["implementations"]
    permutations = generate_permutations(implementations)

    # Prepare the location
    start_time = datetime.datetime.now(datetime.timezone.utc)
    results_dir = start_time.strftime("%Y%m%dT%H%M%SZ")  # Colons can be iffy

    output_dir = Path(args.output_dir)

    if not output_dir.is_absolute():
        output_dir = output_dir.absolute()
    output_dir = output_dir / results_dir

    logger.debug(f"Results directory: {output_dir}")

    if not args.dry_run:
        output_dir.mkdir()

    logger.debug(f"Iterating over {len(permutations)} permutations")

    results = execute_permutations(args, output_dir, permutations)

    # Create JSON file with array of results.
    if not args.dry_run:
        save_results(output_dir, results)


# For each implementation that we know of, based on it having a client and/or
# server, work out permutations of all.
def generate_permutations(impls: Implementations) -> list[Permutation]:
    permutations: list[Permutation] = []
    for server_name, server in impls.items():
        if server["enabled"] and server["server"]:
            for client_name, client in impls.items():
                if client["enabled"] and client["client"]:
                    permutations.append(
                        {
                            "server": server_name,
                            "client": client_name
                        }
                    )
    return permutations


def save_results(output_dir: Path, results: dict[str, dict[str, Result]]):
    flat_results: list[Result] = []

    for s in results:
        for c in results[s]:
            flat_results.append(results[s][c])

    with output_dir.joinpath("result.json").open("w") as f:
        json.dump(flat_results, f, indent=2, sort_keys=True)


def execute_permutations(
    args: argparse.Namespace, output_dir: Path, permutations: list[Permutation]
) -> dict[str, dict[str, Result]]:
    results: dict[str, dict[str, Result]] = defaultdict(dict)

    # Execute permutations with optional concurrency
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = [
            executor.submit(run_permutation, permutation, args, str(output_dir))
            for permutation in permutations
        ]
        for future in as_completed(futures):
            try:
                perm_result = future.result()
            except Exception as exc:
                logger.error("Permutation run raised exception: %s", exc)
                continue

            if perm_result is None:
                continue

            server, client, res = perm_result

            results[server][client] = res
    return results


def run_permutation(
    permutation: Permutation,
    args: argparse.Namespace,
    output_dir: str,
) -> tuple[str, str, Result] | None:
    perm_dir = Path(output_dir).joinpath(
        f"{permutation['server']}_{permutation['client']}"
    )
    logger.debug(
        f"Preparing to run for server: {permutation['server']} client: {permutation['client']}"
    )
    env = {
        "SERVER_IMAGE": f"zeitwaage-{permutation['server']}:latest",
        "CLIENT_IMAGE": f"zeitwaage-{permutation['client']}:latest",
        "PERM_NAME": f"zeitwaage-{permutation['server']}-{permutation['client']}",
        "PERM_DIR": str(perm_dir),
    }

    logger.debug(f"Creating permutation directory {perm_dir}")
    if not args.dry_run:
        perm_dir.mkdir()

    perm_config = os.path.abspath(args.perm_config)
    perm_cmd = f"{args.container} compose -f {perm_config} up"
    logger.debug(f"Running `{perm_cmd}` with a {args.timeout} second timeout...")
    logger.debug(env)

    if args.dry_run:
        logger.info("This is the bit where we pretend to run, but are not!")

    output = subprocess.PIPE
    if args.workers > 1:
        # stdout and stderr gets very loud with more than 1 runner
        output = subprocess.DEVNULL

    perm_process = subprocess.Popen(
        perm_cmd.split(" "), env=env, stdout=output, stderr=output
    )
    try:
        perm_process.wait(float(args.timeout))
    except subprocess.TimeoutExpired:
        perm_process.kill()
        logger.warning(
            f"Terminating server: {permutation['server']} client: {permutation['client']}"
        )
    cleanup_cmd = f"{args.container} compose -f {perm_config} down --remove-orphans"
    logger.debug(f"Running cleanup commmand {cleanup_cmd}")
    subprocess.run(cleanup_cmd.split(" "), env=env, stdout=output, stderr=output)

    return (
        permutation["server"],
        permutation["client"],
        {
            "client": permutation["client"],
            "client_log": "client_log",
            "server": permutation["server"],
            "result": "result",
            "server_log": "server_log",
            "pcap": "pcap",
        },
    )


def packet_tree_str(packet: Any, indent: int = 0) -> str:
    ret = ""
    istr = ""
    if indent > 1:
        istr = "  " * (indent - 1)
    if isinstance(packet, pyroughtime.RoughtimePacket):
        ret += "%s%s\n" % (istr, packet.get_tag_str())
        for t in packet.get_tags():
            ret += packet_tree_str(packet.get_tag(t), indent + 1)
    elif isinstance(packet, pyroughtime.RoughtimeTag):
        vlen = packet.get_value_len()
        if vlen == 4 or vlen == 8:
            val = packet.to_int()
            val = "%d (0x%x)" % (val, val)
        else:
            val = packet.get_value_bytes().hex()
        ret += "%s%s (%3d) Val: %s\n" % (istr, packet.get_tag_str(), vlen, val)
    else:
        raise Exception("Bad tag type.")
    return ret


if __name__ == '__main__':
    main()