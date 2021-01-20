import logging
from models.EntityNode import EntityNode
from services.JikanService import JikanService
from jsonpath_ng.ext import parse # TODO why doesn't this import

logger = logging.getLogger('Person')
BLACKLIST_TERMS = ['funimation', 'sentai', ' adv ']

class Person(EntityNode):
    def __init__(self, entityManager, session, mal_id, name=None):
        EntityNode.__init__(self, entityManager, Person, session, mal_id)
        self.name = name
        self._api_response = None

    @property
    def api_response(self):
        if self._api_response is None:
            self._api_response = JikanService.fetchPerson(self.mal_id)

        return self._api_response

    def collectRelated(self, role):
        return [self.entityManager.Media(id, name) for (id, name) in self.locateRoleInstances(role)]

    def link(self, item, verb):
        self.entityManager.link(self, item, verb)

    def load(self):
        record = self.session.run(f'MATCH (p:{self.nodeType} {{mal_id: $mal_id}}) RETURN p', mal_id=self.mal_id).single()
        if record is None:
            return

        neo_dict = record.data()['p']

        # this approach may become cumbersome if more attributes pile up
        # but for now it's simple and clear
        self.expansion_depth = neo_dict.get('expansion_depth', 0)
        self.name = neo_dict.get('name')
        self.cached = neo_dict.get('cached', False)
        self.expanding = neo_dict.get('expanding', False)
        self.loaded = True

    def locateRoleInstances(self, role):
        expr = parse(f'$.anime_staff_positions[?position="{role}"].anime')
        return [[match.value['mal_id'], match.value['name']] for match in expr.find(self.api_response)]

    def pp(self):
        print(f'<Person mal_id={self.mal_id} name={self.name}>')

    def sync(self, andWrite=False):
        if self.isCached():
            logger.info(f'Not syncing cached person {self.mal_id}')
            return self
        
        self.load()

        if not self.blacklisted:
            raw_about = self.api_response.get('about')
            if raw_about is None:
                raw_about = ''
            about = raw_about.lower()

            for term in BLACKLIST_TERMS:
                if term in about:
                    logger.warn(f'Found forbidden term "{term}"')
                    self.blacklisted = True
                    break

        if not self.blacklisted:
            self.name = self.api_response['name']
            self.cached = True
        
        if self.blacklisted:
            logger.warn(f'Blacklisting node {self.mal_id}')

        if andWrite:
            self.write()

        return self

    def write(self):
        self.touch()
        self.session.write_transaction(lambda tx: tx.run("MATCH (p:Person {mal_id: $mal_id}) SET p={mal_id: $mal_id, name: $name, cached: $cached, expansion_depth: $expansion_depth, blacklisted: $blacklisted, expanding: $expanding}", mal_id=self.mal_id, name=self.name, cached=self.cached, expansion_depth=self.expansion_depth, blacklisted=self.blacklisted, expanding=self.expanding))
