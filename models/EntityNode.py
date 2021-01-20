import logging

BLACKLIST_IDS = [5316, 203]

logger = logging.getLogger('EntityNode')
class EntityNode:
    def __init__(self, entityManager, entityType, session, mal_id):
        self.entityManager = entityManager
        self.session = session
        self.entityType = entityType
        self.blacklisted = False
        self.expanding = False

        self.mal_id = mal_id
        self.expansion_depth = 0
        self.cached = False
        self.loaded = False

        if self.mal_id in BLACKLIST_IDS:
            self.blacklisted = True

    @property
    def nodeType(self):
        return self.entityType.__name__
    
    def collectRelated(self, role):
        raise Exception('Implement in entity derived class')

    def expand(self, depth=1):
        if depth < 1:
            logger.debug(f'Max depth reached; not expanding node {self.mal_id}')
            return
        
        if self.mal_id in BLACKLIST_IDS or self.blacklisted:
            logger.warn(f'Not expanding blacklisted id {self.mal_id}')
            return

        if not self.loaded:
            self.load()
        
        if self.expanding:
            logger.info(f'Skipping reentrant expansion for id {self.mal_id}')
            return
        
        if self.expansion_depth >= depth:
            logger.info(f'Already sufficiently expanded; not re-expanding node {self.mal_id}')
            return

        self.expanding = True
        self.write()

        for (role, verb) in self.entityManager.TRACKED_RELATIONSHIPS:
            for item in self.collectRelated(role):
                item.sync(True)
                self.link(item, verb)
                item.expand(depth-1)

        self.expansion_depth = max(self.expansion_depth, depth)
        self.expanding = False
        self.write()

    def isCached(self):
        response = self.session.run(f'MATCH (p:{self.nodeType} {{mal_id: $mal_id}}) RETURN p.cached', mal_id=self.mal_id)
        record = response.single()
        if record is None:
            return False
        return bool(record.value())
    
    def link(self, item, verb):
        raise Exception('Implement in derived class')

    def touch(self):
        self.session.write_transaction(lambda tx: tx.run(f'MERGE (p:{self.nodeType} {{mal_id: $mal_id}})', mal_id=self.mal_id))

    def write(self):
        raise Exception('You should not try to write an EntityNode')