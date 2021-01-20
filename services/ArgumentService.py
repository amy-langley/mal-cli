import argparse

class ArgumentService:
    parser = None
    args = None

    @classmethod
    def configure(cls):
        if not cls.parser:
            cls.parser = argparse.ArgumentParser(description='Make updates to the mal graph')

            cls.parser.add_argument('operation', help='Operation to be performed on the graph', choices=['clear', 'update', 'load'])

            id_group = cls.parser.add_mutually_exclusive_group()
            id_group.add_argument('-p', '--person', metavar='id', help='Id of person to be updated', nargs='+', type=int)
            id_group.add_argument('-m', '--media', metavar='id', help='Id of media to be updated', nargs='+', type=int)
            id_group.add_argument('-c', '--character', metavar='id', help='Id of character to be updated', type=int)
            id_group.add_argument('-s', '--studio', metavar='id', help='Id of studio to be updated', type=int)

            cls.parser.add_argument('-d', '--depth', help='Depth of related nodes to be retrieved', type=int)
            cls.parser.add_argument('-v', '--verbose', help='Increased verbosity on client operations', action='store_true')

        return cls

    @classmethod
    def parse(cls):
        if not cls.args:
            args = cls.parser.parse_args()

            if args.operation == 'update' and not (args.person or args. media or args.character or args.studio):
                parser.error('You must specify an id to update')

            if args.operation == 'clean' and args.depth:
                parser.error('You should not specify a depth when clearing')

            if args.depth is None:
                args.depth = 1

            cls.args = args

        return cls.args

