from typing import Union, Any


class AnswerGenerator(object):
    def __init__(self):
        self.__content = {}
        self.question_answer_separator: str = '$'
        self.separator: str = '}'

    def __getitem__(self, key: Union[int, str]):
        if key is None:
            raise ValueError('key - Expect NOT None.')
        if isinstance(key, str):
            key = int(key)
        return self.__content.get(key, None)

    def __setitem__(self, key: Union[int, str], value: Any = None):
        if not isinstance(key, (int, str)):
            raise ValueError(f'key - Expect int or str, but got {type(key)}.')
        if value is None:
            raise ValueError('value - Expect NOT None.')
        if isinstance(key, str):
            key = int(key)
        self.__content[key] = value

    def __delitem__(self, key: Union[int, str]):
        self.pop(key)

    def __getattr__(self, name: str):
        # 当属性不存在时
        print(f'{self.__class__.__name__}.{name}:不存在<Return None>')
        self.__content.keys()

    def __call__(self, *args, **kwargs):
        return self.generate()

    def __repr__(self):
        demo_str = "'" + self.generate() + "'"
        length = len(self.__content)
        self.clear()
        return f'<{length} Question(s) : {self.__class__.__name__} DEMO = {demo_str}>'

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.__content)

    def generate(self) -> str:
        self.clear()
        self.rule()
        str_list: list[str] = [f'{k}{self.question_answer_separator}{v}' for k, v in sorted(self.__content.items())]
        return self.separator.join(str_list)

    def rule(self) -> None:
        pass

    def get_content(self) -> dict[Union[int, str], Any]:
        return self.__content

    def get(self, key: Union[int, str], default: Any = None) -> Any:
        if key is None:
            raise ValueError('key - Expect NOT None.')
        if isinstance(key, str):
            key = int(key)
        return self.__content.get(key, default)

    def add(self, index: Union[int, str], answer: Any) -> None:
        self.__setitem__(index, answer)

    def pop(self, key: Union[int, str]) -> Any:
        if key is None:
            return
        if key not in self.__content.keys():
            return
        if isinstance(key, str):
            key = int(key)
        return self.__content.pop(key)

    def keys(self):
        return self.__content.keys()

    def values(self):
        return self.__content.values()

    def items(self):
        return self.__content.items()

    def update(self, other: dict) -> None:
        for k, v in other.items():
            self.add(k, v)

    def clear(self) -> None:
        self.__content.clear()
