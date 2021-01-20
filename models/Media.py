import logging
from jsonpath_ng import parse
from models.EntityNode import EntityNode
from services.JikanService import JikanService

logger = logging.getLogger('Media')

class Media(EntityNode):
    def __init__(self, entityManager, session, mal_id, title=None):
        EntityNode.__init__(self, entityManager, Media, session, mal_id)
        self.title = title
        self._api_response = None
        self._people_api_response = None

    @property
    def people_api_response(self):
        if self._people_api_response is None:
            self._people_api_response = JikanService.fetchContributors(self.mal_id)

        return self._people_api_response

    @property
    def api_response(self):
        if self._api_response is None:
            self._api_response = JikanService.fetchMedia(self.mal_id)

        return self._api_response

    def collectRelated(self, role):
        expr = parse('$.staff[*]')
        all_staff = expr.find(self.people_api_response)
        filtered_staff = filter(lambda item: (role in item.value['positions']), all_staff)
        result = [[match.value['mal_id'], match.value['name']] for match in filtered_staff]
        return [self.entityManager.Person(id, name) for (id, name) in result]

    def link(self, item, verb):
        self.entityManager.link(item, self, verb)

    def load(self):
        record = self.session.run(f'MATCH (p:{self.nodeType} {{mal_id: $mal_id}}) RETURN p', mal_id=self.mal_id).single()
        if record is None:
            return

        neo_dict = record.data()['p']

        # this approach may become cumbersome if more attributes pile up
        # but for now it's simple and clear
        self.expansion_depth = neo_dict.get('expansion_depth', 0)
        self.title = neo_dict.get('title')
        self.cached = neo_dict.get('cached', False)
        self.expanding = neo_dict.get('expanding', False)
        self.loaded = True
    
    def onSync(self):
        self.title = self.api_response['title']

    def onWrite(self, tx):
        tx.run("""
            MATCH (p:Media {mal_id: $mal_id}) 
            SET p={
                mal_id: $mal_id,
                title: $title,
                cached: $cached,
                expansion_depth: $expansion_depth,
                blacklisted: $blacklisted,
                expanding: $expanding
            }""", mal_id=self.mal_id, title=self.title, cached=self.cached, expansion_depth=self.expansion_depth, blacklisted=self.blacklisted, expanding=self.expanding)
