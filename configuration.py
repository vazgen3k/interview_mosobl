import yaml


class Config:
    def get_config():
        with open("config.yaml", "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        return cfg

config = Config.get_config()