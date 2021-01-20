import logging
from services.ArgumentService import ArgumentService

BLACKLIST_IDS = [5316, 203]
FORCE = ArgumentService.parse().force

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
        raise Exception('Implement in derived class')

    def link(self, item, verb):
        raise Exception('Implement in derived class')

    def onLoad(self):
        raise Exception('Implement in derived class')

    def onSync(self):
        raise Exception('Implement in derived class')

    def expand(self, depth=1):
        if depth < 1:
            logger.debug(f'Max depth reached; not expanding node {self.mal_id}')
            return

        if not self.loaded:
            self.load()
        
        if self.mal_id in BLACKLIST_IDS or self.blacklisted:
            logger.warn(f'Not expanding blacklisted id {self.mal_id}')
            return

        if self.expanding:
            logger.info(f'Skipping reentrant expansion for id {self.mal_id}')
            return
        
        if self.expansion_depth >= depth and not FORCE:
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
    
    def load(self):
        record = self.session.run(f'MATCH (n:{self.nodeType} {{mal_id: $mal_id}}) RETURN n', mal_id=self.mal_id).single()
        if record is None:
            return

        neo_dict = record.data()['n']

        self.expansion_depth = neo_dict.get('expansion_depth', 0)
        self.cached = neo_dict.get('cached', False)
        self.expanding = neo_dict.get('expanding', False)

        self.onLoad(neo_dict)

        self.loaded = True
        return self

    def sync(self, andWrite=False):
        if self.isCached() and not FORCE:
            logger.info(f'Not syncing cached {self.nodeType} {self.mal_id}')
            return self
        
        self.load()

        if self.blacklisted:
            logger.warn(f'Not syncing blacklisted {self.nodeType} {self.mal_id}')
            return self

        self.onSync()
        self.cached = True

        if self.blacklisted:
            logger.warn(f'Blacklisting node {self.mal_id}')

        if andWrite:
            self.write()

        return self

    def touch(self):
        self.session.write_transaction(lambda tx: tx.run(f'MERGE (n:{self.nodeType} {{mal_id: $mal_id}})', mal_id=self.mal_id))
        return self

    def write(self):
        self.touch()
        self.session.write_transaction(self._write)
        return self
    
    def _write(self, tx):
        params = {
            'mal_id': self.mal_id,
            'cached': self.cached,
            'expansion_depth': self.expansion_depth,
            'blacklisted': self.blacklisted,
            'expanding': self.expanding,
            **self.prepare()
        }

        s = ', '.join([f'{k}: ${k}' for k in params.keys()])
        cmd = f'MATCH (n:{self.nodeType} {{mal_id: $mal_id}}) SET n={{{s}}}'
        tx.run(cmd, **params)