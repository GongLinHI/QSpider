# QSpider

- 🎉这是一个适用于[问卷星](https://www.wjx.cn/)平台的答卷程序，
- 🎉可以实现任意的数据需求
- ⚠️仅供技术交流与学习使用。您需要完全自行承担使用本程序带来的一切后果！

## 快速上手

1. 确定问卷的`ID`：

   例如：问卷地址[https://w.wjx.com/vm/rXz5Xu9.aspx](https://w.wjx.com/vm/rXz5Xu9.aspx)的`ID`是`rXz5Xu9`

2. 确定问卷`submitdata`的格式/内容，它由问卷的答案编码而来：

   例如：`'1$1}2$测试`，代表着，题目`1`选择第`1`个选项、题目`2`填写的内容为`测试`

   **`submitdata`的格式取决于您的问卷，需要您自行使用抓包解析。**

3. `git clone`本项目，并编写代码，参见[demo1.py](/demo1.py)

   ```python
   from Spider import QSpider
   
   if __name__ == '__main__':
       id = 'rXz5Xu9'
       spider = QSpider(id)
       spider.submit('1$1}2$测试')
   
   ```

   此时控制台若有如下输出即为成功：

   ```
   [2024-05-21 17:53:50] - 已提交 : <Response [200]>
   ```

## 自动生成答卷

我们往往需要短时间内提交若干份答卷，根据自己的需求，编写对应的答案生成器。

您只需继承`AnswerGenerator`并重写其中的`rule()`方法，并在此方法中描述答案生成的逻辑关系。

```python
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
```

并把生成的答案传入`spider.submit()`方法

```python
gen = MyGen()
spider.submit(gen.generate())
```

或

```python
spider.submit(gen()) 
```

完整代码详见[demo2.py](/demo2.py)

- 最后更新于：2024年5月22日
