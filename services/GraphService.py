from neo4j import GraphDatabase
from services.ConfigService import ConfigService

class GraphService:
    graph = None

    @classmethod
    def getGraph(cls):
        if not cls.graph:
            cls.graph = GraphDatabase.driver(ConfigService.neo4jUri, auth=(ConfigService.neo4jUsername, ConfigService.neo4jPassword))

        return cls.graph
