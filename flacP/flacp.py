"""
The main module of program
"""
import argparse
import sys
from flac_parser import Parser
from flac_player import Player

__author__ = 'Skipper'


def main():
    """
    The main function if program
    :return: null
    """
    def _print_options():
        print('0: show general info')
        print('1: show info about any block')
        print('all: show info about every block and every frame'
              + ' (it can take much time)')
        print('play: play this file')
        print('pause: pause the playing')
        print('exit: close program')

    def _choose_block():
        print('Choose block from 0 to ' + str(header.get_blocks_num() - 1)
              + ':')
        block_number = int(input('>>> ').replace(' ', ''))
        if -1 < block_number < header.get_blocks_num():
            header.blocks[block_number].print_info()
        else:
            print('Wrong number')

    def _print_all():
        for block in header.blocks:
            block.print_info()
        local_frames = parser.parse_frames()
        for frame in local_frames:
            frame.print_info()

    arg_parser = argparse.ArgumentParser(
        description='flac parser by Skipper95')
    arg_parser.add_argument('filename', metavar='N', type=str, nargs=1,
                            help='flac file name')
    arg_parser.add_argument("-a", "--all", action="store_true",
                            help="print all info about file")
    arg_parser.add_argument("-g", "--gen", action="store_true",
                            help="print general information about file")
    args = arg_parser.parse_args()
    try:
        with open(args.filename[0], 'rb') as f:
            raw_bytes = f.read()
    except FileNotFoundError:
        print('File not found', file=sys.stderr)
        exit(-1)
    except PermissionError:
        print('Permission denied', file=sys.stderr)
        exit(-2)
    except Exception:
        print('Something wrong', file=sys.stderr)
        exit(-3)
    parser = Parser(raw_bytes)
    header = parser.parse_header()
    if not header:
        print('File is not flac', file=sys.stderr)
        exit(-5)
    player = Player(args.filename[0], 100)
    actions = {'0': header.print_stream_info,
               '1': _choose_block,
               'all': _print_all,
               'play': player.play,
               'pause': player.pause}
    if args.all:
        actions['all']()
    elif args.gen:
        actions['0']()
    else:
        print('There is ' + str(header.get_blocks_num()) + ' blocks in header')
        print('So, what do you want to know?')
        _print_options()
        command = input('>>> ').replace(' ', '')
        while command != 'exit':
            if command in actions.keys():
                actions[command]()
            else:
                print('Wrong command')
            _print_options()
            command = input('>>> ').replace(' ', '')


if __name__ == "__main__":
    main()
