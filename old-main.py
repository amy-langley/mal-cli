from models.EntityManager import EntityManager
from services.GraphService import GraphService
from services.LogService import LogService

BLACKLIST_IDS = [5316, 203]

LogService.configure()

with EntityManager.initialize(GraphService.getGraph()):
    EntityManager.Person(40830).sync(True).expand(4)

    for id in [30, 145, 227, 2001]:
        EntityManager.Media(id).sync(True).expand(3)
