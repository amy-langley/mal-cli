import logging
from models.Person import Person
from models.Media import Media

logger = logging.getLogger('EntityMgr')

class EntityManager:
    TRACKED_RELATIONSHIPS = [
        ['Director', 'DIRECTED'],
        ['Producer', 'PRODUCED'],
#       ['Executive Producer', 'PRODUCED'],
#       ['Key Animation', 'ANIMATED'],
#       ['Animation Director', 'ANIMATED'],
#       ['Storyboard', 'ANIMATED'],
        # ['Script', 'WROTE'],
#       ['Screenplay', 'WROTE']
    ]

    @classmethod
    def initialize(cls, driver):
        cls.session = driver.session()
        return EntityManagerHandle(cls.session)

    @classmethod
    def clear(cls):
        cls.session.write_transaction(lambda tx: tx.run("MATCH (n) DETACH DELETE n"))

    @classmethod
    def link(cls, entity1, entity2, relationship):
        if entity1.blacklisted:
            logger.warn(f'Not linking blacklisted id {entity1.mal_id}')
        if entity2.blacklisted:
            logger.warn(f'Not linking blacklisted id {entity2.mal_id}')
        if entity1.blacklisted or entity2.blacklisted:
            return

        cls.session.write_transaction(lambda tx: tx.run(
            f'MATCH (e1:{entity1.nodeType} {{mal_id: $e1_mal_id}}), (e2:{entity2.nodeType} {{mal_id: $e2_mal_id}})'
            f'MERGE (e1)-[:{relationship}]->(e2)',
            e1_mal_id=entity1.mal_id, e2_mal_id=entity2.mal_id, relationship=relationship
        )) 

    @classmethod
    def Person(cls, id, name=None):
        return Person(cls, cls.session, id, name)

    @classmethod
    def Media(cls, id, name=None):
        return Media(cls, cls.session, id, name)


class EntityManagerHandle:
    def __init__(self, session):
        self.session = session

    def __enter__(self):
        pass

    def __exit__(self, a, b, c):
        self.session.close()

