# import random
# from QSpider import QSpider
#
# if __name__ == '__main__':
#     id = 'rXz5Xu9'
#     for i in range(1, 100):
#         spider = QSpider(id)
#         t = random.randrange(5, 15)
#         time.sleep(t)
#         spider.submit(r'1$1}2$测试【1】' + f'{i}')
from QSpider import QSpider

if __name__ == '__main__':
    id = 'rXz5Xu9'
    spider = QSpider(id)
    spider.submit('1$1}2$测试')
