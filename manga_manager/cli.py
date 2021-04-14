"""Console script for manga_manager."""
import sys
import traceback

from manga_manager import __version__
import manga_manager.manga_manager as mm
from manga_manager.provider import *
from argparse import ArgumentParser


def cl():
    """Command line or start menu"""

    return len(sys.argv) > 1


def argument_parser():
    parser = ArgumentParser()
    parser.add_argument("action", choices=["add", "remove", "edit", "read", "list", "quit"])
    parser.add_argument("title", nargs="*")
    parser.add_argument("-c", "--chapters", required=False)
    parser.add_argument(
        "-dm", "--download_mode", choices=["dynamic", "all", "none"], default="dynamic"
    )
    parser.add_argument("-p", "--provider", default="Mangakakalot")
    return parser


def print_separator():
    """Prints a separator line"""

    print("~" * 35)


def print_welcome():
    """Prints the manga_manager welcome header"""

    welcome_message = "~Welcome to Manga Manager~"
    print_separator()
    print(welcome_message)
    print("-" * len(welcome_message) + "\n")


def main():
    """Console script for manga_manager."""
    if cl() and sys.argv[1] in ["-v", "--version"]:
        print(__version__)
        return
    else:
        manager = mm.MangaManager()
        new = manager.new_chapters()
        count = 1 if cl() else -1
        try:
            while abs(count) > 0:
                print_welcome()
                manager.list_manga(new)
                command = input("> ").split() if not cl() else sys.argv[1:]
                parser = argument_parser()
                args = parser.parse_args(command)
                args.title = " ".join(args.title)
                if args.action == "add":
                    print_separator()
                    manager.add_manga(
                        title=args.title,
                        provider=args.provider,
                        download_mode=args.download_mode,
                    )
                    manager.save()
                elif args.action == "remove":
                    manager.remove_manga(args.title)
                    manager.save()
                elif args.action == "edit":
                    print_separator()
                    manager.edit_manga(args.title)
                    manager.save()
                elif args.action == "read":
                    print_separator()
                    manager.read_manga(
                        title=args.title,
                        chapter=int(args.chapters) - 1 if args.chapters else None,
                    )
                    manager.save()
                elif args.action == "quit":
                    break
                count -= 1
        except KeyboardInterrupt:
            """do nothing"""
        except Exception:
            traceback.print_exc()
        finally:
            manager.save()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
