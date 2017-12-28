from argparse import ArgumentParser, Namespace


def parse_argv() -> Namespace:
    parser = ArgumentParser(description="Generate system configuration")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_argv()
