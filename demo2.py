import random
import time

from AnswerGenerator import AnswerGenerator
from Spider import QSpider


class MyGen(AnswerGenerator):

    def __init__(self):
        super().__init__()

    def rule(self):
        """
        重写这个函数，描述所需要的规则。

        :return: None
        """
        # Q1 随机
        if random.random() > 0.5:
            self.add(1, 1)
        else:
            self.add(1, 2)
        # Q2
        self.add(2, f'Test:{time.time()}')

        # '1$1}2$Test:1716351595.7801666'


if __name__ == '__main__':
    id = 'rXz5Xu9'
    gen = MyGen()
    for i in range(100):
        spider = QSpider(id)
        spider.submit(gen.generate())  # spider.submit(gen()) 亦可
