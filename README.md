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

3. `git clone`本项目，并编写代码，参见[Demo.py](/demo.py)

   ```python
   from QSpider import QSpider
   
   if __name__ == '__main__':
       id = 'rXz5Xu9'
       spider = QSpider(id)
       spider.submit('1$1}2$测试')
   
   ```

   此时控制台若有如下输出即为成功：

   ```
   [2024-05-21 17:53:50] - 已提交 : <Response [200]>
   ```




- 最后更新于：2024年5月21日
