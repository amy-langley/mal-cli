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

    def onLoad(self, neo_dict):
        self.name = neo_dict.get('name')

    def locateRoleInstances(self, role):
        expr = parse(f'$.anime_staff_positions[?position="{role}"].anime')
        return [[match.value['mal_id'], match.value['name']] for match in expr.find(self.api_response)]

    def onSync(self):
        self.name = self.api_response['name']
        raw_about = self.api_response.get('about')
        if raw_about is None:
            raw_about = ''
        about = raw_about.lower()

        for term in BLACKLIST_TERMS:
            if term in about:
                logger.warn(f'Found forbidden term "{term}"')
                self.blacklisted = True
                break

    def pp(self):
        print(f'<Person mal_id={self.mal_id} name={self.name}>')
    
    def prepare(self):
        return {
            'name': self.name,
        }