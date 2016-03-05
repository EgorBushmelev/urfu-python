"""
CustomPEP8 - my implementation of PEP8 validator
"""
import argparse
import os
import sys
from validator import Validator

__author__ = 'Skipper'


def main():
    """
    Main function of script
    :return:
    """

    def _parse_file(file):
        """
        The function parse file by path.
        :param file: str
        :return: list
        """
        try:
            with open(file, encoding='utf-8', errors='replace') as opened_file:
                return Validator(opened_file.readlines()).validate()
        except FileNotFoundError:
            print(file + ' not found', file=sys.stderr)

    parser = argparse.ArgumentParser(description='Custom PEP8 validator')
    parser.add_argument('filename', metavar='N', type=str, nargs='*',
                        help='the name of file or directory to be checked')
    args = parser.parse_args()
    out = []
    if not args.filename:
        source = []
        for line in sys.stdin:
            source.append(line)
        errors = Validator(source).validate()
        out.append((errors, 'stdin'))
    elif os.path.isdir(args.filename[0]):
        if os.path.exists(args.filename[0]):
            directory = args.filename[0]
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if os.path.splitext(file)[-1] == '.py':
                        full_name = os.path.join(root, file)
                        out.append((_parse_file(full_name), full_name))
        else:
            print(args.filename[0] + ' not found', file=sys.stderr)
    else:
        for file in args.filename:
            result = _parse_file(file)
            if result:
                out.append((result, file))
    if len(out):
        for file, file_name in out:
            for key in sorted(file.keys()):
                for value in file.get(key):
                    print('{}:{}:{}:{}'.format(file_name, str(key+1),
                                               value[0], value[1].value))


if __name__ == '__main__':
    main()
