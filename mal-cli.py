from models.EntityManager import EntityManager

from services.ArgumentService import ArgumentService
from services.ConfigService import ConfigService
from services.GraphService import GraphService
from services.LogService import LogService

LogService.configure()
args = ArgumentService.configure().parse()

with EntityManager.initialize(GraphService.getGraph()):
    if args.operation == 'clear':
        EntityManager.clear()

    if args.operation == 'update':
        depth = args.depth
        if args.person:
            for id in args.person:
                EntityManager.Person(id).sync(True).expand(depth)
        if args.media:
            for id in args.media:
                EntityManager.Media(id).sync(True).expand(depth)

    if args.operation == 'load':
        for id in args.person:
            p = EntityManager.Person(id)
            p.load()
            p.pp()