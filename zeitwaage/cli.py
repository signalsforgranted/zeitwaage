from argparse import ArgumentParser


def main() -> None:
    parser = ArgumentParser()

    parser.add_argument(
        "--verbose", action=argparse.BooleanOptionalAction, help="Enable greater verbosity"
    )
    parser.add_argument(
        "--output-dir", default="results/", help="Base directory to write data out to"
    )
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        help="Don't make any system calls, just print commands out",
    )
    parser.add_argument(
        "--container",
        type=str,
        default="/usr/local/bin/docker",
        help="Path to docker or your preferred container manager",
    )
    
    args = parser.parse_args()

if __name__ == '__main__':
    main()