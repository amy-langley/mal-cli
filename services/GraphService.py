from neo4j import GraphDatabase

# todo read from yml or env or something
neo4j_uri = "neo4j://cocona.local:7687"
driver = GraphDatabase.driver(neo4j_uri, auth=("neo4j", "neo4j"))

class GraphService:
    graph = None

    @classmethod
    def getGraph(cls):
        if not cls.graph:
            cls.graph = GraphDatabase.driver(neo4j_uri, auth=('neo4j', 'neo4j'))

        return cls.graph
