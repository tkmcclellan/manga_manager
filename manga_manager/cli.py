"""Console script for manga_manager."""
import argparse
import sys

import manga_manager.manga_manager as mm


def main():
    """Console script for manga_manager."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    mm.start_menu()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
