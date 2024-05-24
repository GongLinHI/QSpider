import copy
import random
from abc import abstractmethod
from collections.abc import Iterable, Sized
from enum import Enum
from typing import Union, Any, TypeVar, Type

import numpy as np


class ReturnType(Enum):
    """
    这是AnswerGenerator部分函数的返回值类型
    - ReturnType.LIST 表明总是返回list
    - ReturnType.DYNAMIC 表明：
        - 若k=1，则返回单个值
        - 否则，返回list
    - ReturnType.NDARRAY 表明总是返回np,ndarray

    建议使用ReturnType.LIST
    """
    LIST = list
    DYNAMIC = (int, float, list)
    NDARRAY = np.ndarray


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
        if key <= 0:
            raise ValueError('key/index must be positive.')
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

    @abstractmethod
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

    def update(self, other: dict):
        for k, v in other.items():
            self.add(k, v)

    def clear(self):
        self.__content.clear()

    @staticmethod
    def sort(iterable, *, key=None, desc=False):
        """
        根据给定的key和desc参数对iterable进行排序（默认升序，desc=False）。

        :param iterable: 需要排序的可迭代对象。
        :param key: 排序的键。如果为None或者可调用对象，则直接用作sorted函数的key参数。
                     如果为与iterable长度相同的可迭代对象，则将其与iterable的元素进行配对，并根据key进行排序。
                     默认为None。
        :param desc: 是否降序排序。默认为False。
        :return: 排序后的iterable，其类型与输入iterable的类型相同（如果可能）。
        :raise ValueError: 如果key为可迭代对象，但其长度与iterable的长度不同时引发。
        :raise TypeError: 如果key既不是可调用对象也不是与iterable长度相同的可迭代对象时引发。
        """

        if (key is None) or callable(key):
            return sorted(iterable, key=key, reverse=desc)
        elif isinstance(key, Iterable) and isinstance(key, Sized):
            if len(iterable) != len(key):
                raise ValueError("The length of iterable and key must be the same.")
            # Zip the key and iterable, sort by key, and extract the sorted iterable elements
            sorted_pairs = sorted(zip(key, iterable), reverse=desc)
            sorted_iterable = [element for _, element in sorted_pairs]
        else:
            raise TypeError("Key must be either a callable or an iterable with the same length as the iterable.")

        return type(iterable)(sorted_iterable)

    @staticmethod
    def sample(iterable, weights=None, size=1, *, replace=False, return_type: ReturnType = ReturnType.LIST):
        """
        依据iterable和相应的权重weights进行无放回（默认）抽样。

        :param iterable: 候选的可迭代对象
        :param weights: 各个元素的权重
        :param size: 输出形状。如果给定的形状是，(m, n, k)，那么会抽取 m * n * k 个样本。默认为 1。
        :param replace: 是否进行又有放回抽样，默认是False
        :param return_type: 返回值类型，默认为ReturnType.LIST，即总是返回list，详见ReturnType
        :return: 抽样结果
        """
        if weights is None:
            # 如果没有提供权重，则所有元素的权重相同
            weights = np.ones_like(iterable, dtype=float)
        elif not isinstance(weights, np.ndarray):
            weights = np.array(weights)

        # 确保权重数组与人口数组的长度相同
        if len(iterable) != len(weights):
            raise ValueError("The lengths of population and weights must be the same.")

        # 使用numpy的choice函数进行无放回抽样
        samples = np.random.choice(iterable, size=size, replace=replace, p=weights / weights.sum())

        if return_type == ReturnType.NDARRAY:
            return samples
        elif return_type == ReturnType.LIST or (return_type == ReturnType.DYNAMIC and size != 1):
            return samples.tolist()
        elif return_type == ReturnType.DYNAMIC and size == 1:
            return samples[0]

    @staticmethod
    def generate_normal_random(mu=0.0, sigma=1.0, size=1, dtype=float, *, return_type: ReturnType = ReturnType.LIST):
        """
        生成符合正态分布的随机数。
        :param mu: 正态分布的均值。
        :param sigma: 正态分布的标准差。
        :param size: 输出形状。如果给定的形状是，(m, n, k)，那么会抽取 m * n * k 个样本。默认为 1。
        :param dtype: 输出样本的数据类型。可以是 int 或 float。
        :param return_type: 返回值类型，默认为ReturnType.LIST，即总是返回list，详见ReturnType
        :return: 从正态分布中抽取的随机数。
        """
        # 从正态分布中生成浮点数样本
        samples = np.random.normal(mu, sigma, size)

        # 如果数据类型是 int，则将样本四舍五入并转换为整数类型
        if dtype != float and dtype is not None:
            samples = samples.astype(dtype)

        if return_type == ReturnType.NDARRAY:
            return samples
        elif return_type == ReturnType.LIST or (return_type == ReturnType.DYNAMIC and size != 1):
            return samples.tolist()
        elif return_type == ReturnType.DYNAMIC and size == 1:
            return samples[0]

    @staticmethod
    def generate_poisson_random(lam=1.0, size=1, *, dtype=int, return_type: ReturnType = ReturnType.LIST):
        """
        生成符合泊松分布的随机数。
        :param lam: 泊松分布的参数λ（lambda），即事件发生的平均次数。
        :param size: 输出形状。如果给定的形状是，(m, n, k)，那么会抽取 m * n * k 个样本。默认为 1。
        :param dtype: 输出样本的数据类型。可以是 int 或 float，但泊松分布通常用于整数计数，因此建议使用 int。
        :param return_type: 返回值类型，默认为ReturnType.LIST，即总是返回list，详见ReturnType
        :return: 从泊松分布中抽取的随机数。
        """
        # 从泊松分布中生成样本
        samples = np.random.poisson(lam=lam, size=size)

        # 因为泊松分布本身就是整数分布，所以不需要类型转换
        # 但如果dtype被指定为float，我们仍然可以转换为float类型
        if dtype != int and dtype is not None:
            samples = samples.astype(dtype)

        if return_type == ReturnType.NDARRAY:
            return samples
        elif return_type == ReturnType.LIST or (return_type == ReturnType.DYNAMIC and size != 1):
            return samples.tolist()
        elif return_type == ReturnType.DYNAMIC and size == 1:
            return samples[0]

    @staticmethod
    def generate_binomial_random(n, p, size=1, *, dtype=int, return_type: ReturnType = ReturnType.LIST):
        """
        生成符合二项分布的随机数。
        :param n: 试验次数
        :param p: 每次试验成功的概率
        :param size: 输出形状。如果给定的形状是，(m, n, k)，那么会抽取 m * n * k 个样本。默认为 1。
        :param dtype: 输出样本的数据类型。通常是 int，因为二项分布是整数计数的。
        :param return_type: 返回值类型，默认为ReturnType.LIST，即总是返回list，详见ReturnType
        :return: 从二项分布中抽取的随机数。
        """
        # 从二项分布中生成样本
        samples = np.random.binomial(n=n, p=p, size=size)

        # 如果需要转换为float类型
        if dtype != int and dtype is not None:
            samples = samples.astype(dtype)

        if return_type == ReturnType.NDARRAY:
            return samples
        elif return_type == ReturnType.LIST or (return_type == ReturnType.DYNAMIC and size != 1):
            return samples.tolist()
        elif return_type == ReturnType.DYNAMIC and size == 1:
            return samples[0]

    @staticmethod
    def generate_exponential_random(scale=1.0, size=1, *, dtype=float, return_type: ReturnType = ReturnType.LIST):
        """
        生成符合指数分布的随机数。
        :param scale: 指数分布的比例参数（λ的倒数，即1/λ），也称为尺度参数。
        :param size: 输出形状。如果给定的形状是，(m, n, k)，那么会抽取 m * n * k 个样本。默认为 1。
        :param dtype: 输出样本的数据类型。默认为 float。
        :param return_type: 返回值类型，默认为ReturnType.LIST，即总是返回list，详见ReturnType
        :return: 从指数分布中抽取的随机数。
        """
        # 从指数分布中生成样本
        samples = np.random.exponential(scale=scale, size=size)

        # 如果dtype被指定且不是float，则进行类型转换（但通常指数分布使用float）
        if dtype != float and dtype is not None:
            samples = samples.astype(dtype)

        if return_type == ReturnType.NDARRAY:
            return samples
        elif return_type == ReturnType.LIST or (return_type == ReturnType.DYNAMIC and size != 1):
            return samples.tolist()
        elif return_type == ReturnType.DYNAMIC and size == 1:
            return samples[0]

    @staticmethod
    def generate_gamma_random(shape, scale=1.0, size=1, *, dtype=float, return_type: ReturnType = ReturnType.LIST):
        """
        生成符合伽马分布的随机数。
        :param shape: 伽马分布的形状参数（k，也称为α）。
        :param scale: 伽马分布的比例参数（θ，也称为β），也可以认为是1/λ。
        :param size: 输出形状。如果给定的形状是，(m, n, k)，那么会抽取 m * n * k 个样本。默认为 1。
        :param dtype: 输出样本的数据类型。默认为 float。
        :param return_type: 返回值类型，默认为ReturnType.LIST，即总是返回list，详见ReturnType
        :return: 从伽马分布中抽取的随机数。
        """

        # 从伽马分布中生成样本
        samples = np.random.gamma(shape=shape, scale=scale, size=size)

        # 如果dtype被指定且不是float，则进行类型转换（但通常伽马分布使用float）
        if dtype != float and dtype is not None:
            samples = samples.astype(dtype)

        if return_type == ReturnType.NDARRAY:
            return samples
        elif return_type == ReturnType.LIST or (return_type == ReturnType.DYNAMIC and size != 1):
            return samples.tolist()
        elif return_type == ReturnType.DYNAMIC and size == 1:
            return samples[0]

    @staticmethod
    def generate_f_random(d1, d2, size=1, *, dtype=float, return_type: ReturnType = ReturnType.LIST):
        """
        生成符合F分布的随机数。
        :param d1: 分子项的自由度（通常为正态分布的样本大小减1）。
        :param d2: 分母项的自由度（通常为正态分布的样本大小减1）。
        :param size: 输出形状。如果给定的形状是，(m, n, k)，那么会抽取 m * n * k 个样本。默认为 1。
        :param dtype: 输出样本的数据类型。默认为 float。
        :param return_type: 返回值类型，默认为ReturnType.LIST，即总是返回list，详见ReturnType
        :return: 从F分布中抽取的随机数。
        """
        # 从F分布中生成样本
        samples = np.random.f(d1, d2, size=size)

        # 如果dtype被指定且不是float，则进行类型转换（但通常F分布使用float）
        if dtype != float and dtype is not None:
            samples = samples.astype(dtype)

        if return_type == ReturnType.NDARRAY:
            return samples
        elif return_type == ReturnType.LIST or (return_type == ReturnType.DYNAMIC and size != 1):
            return samples.tolist()
        elif return_type == ReturnType.DYNAMIC and size == 1:
            return samples[0]

    @staticmethod
    def generate_list(stop: int, *, rType=list):
        return AnswerGenerator._generate_list(1, stop, rType=rType)

    @staticmethod
    def generate_list(start: int, stop: int, step: int = 1, *, rType=list):
        return AnswerGenerator._generate_list(start, stop, step, rType=rType)

    @staticmethod
    def _generate_list(start: int, stop: int, step: int = 1, *, rType=list):
        """
        获取特定的列表/元组，作为候选项
        :param start: 起始值
        :param stop: 终止值（包含此值）
        :param step: 步长
        :param rType: 返回值的类型，默认为list
        :return:
        """

        return type(rType)(range(start, stop + 1, step))

    def single_selection(self, index: int, option_num: int, weights=None):
        if not isinstance(option_num, int):
            raise TypeError('option_num must be int.')
        if option_num <= 0:
            raise ValueError('option_num must be positive.')
        if option_num != len(weights):
            raise ValueError('The lengths of weights must equal to option_num.')
        self.add(index, random.choices(range(1, option_num + 1), weights, k=1)[0])

    def single_selection(self, index: int, ans):
        self.add(index, ans)

    def multi_selection(self, index: int, ans):
        if isinstance(ans, (str, int)):
            self.add(index, ans)
        elif isinstance(ans, (list, tuple)):
            ans = [str(x) for x in ans]
            self.add(index, '|'.join(ans))

    def fill_blanks(self, index: int, text: str = ''):
        self.add(index, text)

    @staticmethod
    def shuffle_list(lst: list, *, inplace: bool = True):
        if not isinstance(lst, list):
            raise TypeError('lst must be list.')

        if inplace:  # 原地打乱列表
            random.shuffle(lst)
        else:
            shuffled_lst = copy.deepcopy(lst)
            random.shuffle(shuffled_lst)
            return shuffled_lst


T = TypeVar('T', bound=AnswerGenerator)
AnswerGeneratorType = Type[T]
