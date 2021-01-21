import os
import yaml

class ConfigMetaclass(type):
    config = None

    def load(cls):
        if not cls.config:
            root_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
            yaml_path = os.path.join(root_dir, 'config/mal-cli.yml')
            with open(yaml_path) as file:
                cls.config = yaml.full_load(file)
    
    @property
    def jikanUri(cls):
        cls.load()
        return cls.config['jikan']['uri']

    @property
    def jikanThrottle(cls):
        cls.load()
        return cls.config['jikan']['throttle']
    
    @property
    def neo4jUri(cls):
        cls.load()
        return cls.config['neo4j']['uri']

    @property
    def neo4jUsername(cls):
        cls.load()
        return cls.config['neo4j']['username']

    @property
    def neo4jPassword(cls):
        cls.load()
        return cls.config['neo4j']['password']
    
    @property
    def blacklistIds(cls):
        cls.load()
        return cls.config['blacklist']['ids']
    
    @property
    def blacklistTerms(cls):
        cls.load()
        return cls.config['blacklist']['terms']

class ConfigService(metaclass=ConfigMetaclass):
    pass
