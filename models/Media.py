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

    def onLoad(self, neo_dict):
        self.title = neo_dict.get('title')

    def onSync(self):
        self.title = self.api_response['title']
        self.title_english = self.api_response['title_english']
        self.year_start = self.api_response['aired']['prop']['from']['year']

    def prepare(self):
        return {
            'title': self.title,
            'title_english': self.title_english,
            'year_start': self.year_start
        }
