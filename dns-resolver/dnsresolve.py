"""
Main module is frontend of dns-resolver.
"""
__author__ = 'Skipper'
DEFAULT_PORT = 53
DEFAULT_SERVER = '8.8.8.8'
DEFAULT_TIMEOUT = 5
DEFAULT_NUM_OF_RETRIES = 4
import argparse
from resolver import Resolver


def main():
    parser = argparse.ArgumentParser(description='YOBAdns-resolver')
    parser.add_argument(
        "address", metavar="Address", nargs="+", type=str,
        help='Address that you need to resolve')
    parser.add_argument(
        "--server", "-s", metavar="Server", nargs="?", type=str,
        default=DEFAULT_SERVER,
        help='Set the DNS server to first request, default: 8.8.8.8'
    )
    parser.add_argument(
        "--port", "-p", metavar="Port", nargs="?", type=int,
        default=DEFAULT_PORT,
        help='Set the port of dedicated DNS server'
    )
    parser.add_argument("-d", "--debug", action="store_true",
                        help="switch on debug mode")
    parser.add_argument("-n", "--num", nargs="?", type=int,
                        default=DEFAULT_NUM_OF_RETRIES,
                        help="number of retries")
    parser.add_argument("-w", "--waiting", nargs="?", type=int,
                        default=DEFAULT_TIMEOUT,
                        help="waiting time of request")

    args = parser.parse_args()
    ##############################################
    resolver = Resolver(args.server, args.debug,
                        args.port, args.num, args.waiting)
    received = resolver.resolve(args.address[0])
    if received == resolver.NO_RESPONSE:
        print('\tNo response')
    else:
        if received == resolver.NAME_NOT_FOUND:
            print('\t\tName {} does not exist'.format(args.address[0]))
        else:
            print('\tDomain: ' + args.address[0])
            print('\tResponses:')
            for response in received:
                print('\t\t{}\t{}'.format(resolver.TYPES[response[0]],
                                          response[1]))


if __name__ == '__main__':
    main()
