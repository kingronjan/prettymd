import sys

from argparse import ArgumentParser
from prettymd import format, format_file


def main():
    parser = ArgumentParser()
    parser.add_argument('args', metavar='ARG', type=str, nargs='*')
    parser.add_argument('-f --file', dest='file', type=str)
    parser.add_argument('-o --output', dest='output', default='stream')
    parser.add_argument('-r --reindex-headers', dest='reindex_headers', action='store_true', default=False)
    parser.add_argument('-p --py-prompt', dest='py_prompt', default='shell')
    parser.add_argument('-n --newline-between-headers', dest='newline_between_headers', action='store_true', default=False)
    parser.add_argument('-s --style', dest='style', default=None)

    args = parser.parse_args(args=sys.argv[1:])
    kwargs = dict(output=args.output,
                  style=args.style,
                  reindex_headers=args.reindex_headers,
                  py_prompt=args.py_prompt,
                  newline_between_headers=args.newline_between_headers)

    if args.file:
        format_file(args.file, **kwargs)
    elif args.args:
        for content in args.args:
            format(content, **kwargs)
    else:
        print('No content specified.')
        sys.exit(1)


if __name__ == '__main__':
    main()
