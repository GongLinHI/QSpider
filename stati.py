import math


class Statistics(object):
    def __init__(self, variable_name: str):
        self.name: str = variable_name
        self._data: list = []

    def append(self, *values):
        for x in values:
            self._data.append(x)

    def extend(self, *exts):
        for ls in exts:
            self._data.extend(ls)

    def pop(self, *index):
        ret = []
        for i in index:
            ret.append(self._data.pop(i))
        return ret if len(index) > 1 else ret[0]

    def clear(self):
        self._data.clear()

    @property
    def sum(self):
        return sum(self._data)

    @property
    def mean(self):
        return self.sum / self.length if self.length != 0 else 0.0

    def __len__(self):
        return len(self._data)

    @property
    def length(self):
        return self.__len__()

    @property
    def variance(self):
        if self.length == 0:
            return 0.0
        mean_val = self.mean
        variance_sum = sum((x - mean_val) ** 2 for x in self._data)
        return variance_sum / self.length

    @property
    def standard_deviation(self):
        return math.sqrt(self.variance)

    def __repr__(self):
        return (f'<Variable {self.name} : '
                f'length = {self.length}, '
                f'sum = {self.sum}, '
                f'mean = {self.mean},'
                f'variance = {self.variance}, '
                f'standard deviation = {self.standard_deviation}>')


if __name__ == '__main__':
    print(Statistics('test'))
