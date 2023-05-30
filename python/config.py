import tomllib


class Config(dict):
    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v if not isinstance(v, dict) else Config(v)
        if kwargs:
            for k, v in kwargs.items():
                self[k] = v if not isinstance(v, dict) else Config(v)

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

    @staticmethod
    def from_toml_file(filename):
        with open(filename, "rb") as f:
            data = tomllib.load(f)
        return Config(data)
