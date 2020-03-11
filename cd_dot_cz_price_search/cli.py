"""Console script for cd_dot_cz_price_search."""
import argparse
import sys


def main():
    """Console script for cd_dot_cz_price_search."""
    parser = argparse.ArgumentParser()
    parser.add_argument("_", nargs="*")
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print(
        "Replace this message by putting your code into "
        "cd_dot_cz_price_search.cli.main"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
