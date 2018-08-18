

class Struct(object):
    def __init__(self, d):
        for key, value in d.items():
            if isinstance(value, (list, tuple)):
                setattr(
                    self,
                    key,
                    [
                        Struct(item) if isinstance(item, dict)
                        else item
                        for item in value
                    ]
                )
            else:
                setattr(
                    self,
                    key,
                    Struct(value) if isinstance(value, dict) else value)


if __name__ == "__main__":

    foo = {'a': 1, 'b': {'c': 2}, 'd': ["hi", {'foo': "bar"}]}
    bar = Struct(foo)
    print(foo)
    print(bar)
