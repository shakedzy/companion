from __future__ import annotations
import yaml

class Config(dict):
    """
    This class holds the configuration of the app, stored on files such as `config.yml` or `keys.yml`
    """
    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Config, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Config, self).__delitem__(key)
        del self.__dict__[key]

    def update(self, *args, **kwargs) -> None:
        """
        Add values to config

        :param args: values to be added, must be dicts
        :param kwargs: key-value pairs of configurations to add
        """
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v if not isinstance(v, dict) else Config(v)
        if kwargs:
            for k, v in kwargs.items():
                self[k] = v if not isinstance(v, dict) else Config(v)

    @staticmethod
    def from_yml_file(filename: str) -> Config:
        """
        Create a new Config from a yml file

        :param filename: path to yml file
        :return: Config
        """
        with open(filename, "r") as f:
            data = yaml.safe_load(f)
        return Config(data)

    def update_from_yml_file(self, filename: str) -> None:
        """
        add configurations from yml file

        :param filename: path to yml file
        """
        with open(filename, "r") as f:
            data = yaml.safe_load(f)
        self.update(data)
