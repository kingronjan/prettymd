prettymd
--------


A tool that formats markdown text in Chinese.


Install
-------

- 从 pypi 安装
    ```shell
    pip install prettymd
    ```


Features
--------


- 在中英文之间添加空格
    ```shell
    $ python -m prettymd "我是中文nihao呀"
    我是中文 nihao 呀
    ```

- 将英文变为代码风格。指定 style = 'code'，将英文用反引号包裹起来
    ```shell
    $ python -m prettymd "我是中文nihao呀" -s code
    我是中文 `nihao` 呀
    ```

- 从文件读取内容
    ```shell
    $ cat .\tests\testfile.md
    摘要算法就是通过摘要函数f()对任意长度的数据data计算出固定长度的摘要digest，目的是为了发现原始数据是否被人篡改过。

    $ python -m prettymd -f .\tests\testfile.md
    摘要算法就是通过摘要函数 f() 对任意长度的数据 data 计算出固定长度的摘要 digest，目的是为了发现原始数据是否被人篡改过。
    ```

- 输出到指定文件
    ```shell
    $ # -o 指定输出文件路径
    $ python -m prettymd -f .\tests\testfile.md -o testfile.md

    $ cat testfile.md
    摘要算法就是通过摘要函数 f() 对任意长度的数据 data 计算出固定长度的摘要 digest，目的是为了发现原始数据是否被人篡改过。
    ```

- 代码调用
    ```python
    >>> from prettymd import format
    >>> format('这是一个示例rst文档')
    '这是一个实例 rst 文档'

    >>> from prettymd import format
    >>> format('这是一个示例rst文档', style='code')
    '这是一个实例 `rst` 文档'

    >>> # 为标题添加索引
    >>> from prettymd import format
    >>> print(format("""
    ## h2
    ### h3
    ## h22
    #### h4
    """))

    ## 1. h2
    ### 1.1. h3
    ## 2. h22
    #### 2.0.1. h4
    ```
