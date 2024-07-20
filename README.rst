====
meli
====






A tool that formats markdown text in Chinese.


Features
--------


- 在中英文之间添加空格

.. code-block:: python
    >>> from meli import format
    >>> format('这是一个示例rst文档')
    '这是一个实例 rst 文档'


- 将英文变为代码风格。指定 style = 'code'，将英文用反引号包裹起来
.. code-block:: python
    >>> from meli import format
    >>> format('这是一个示例rst文档', style='code')
    '这是一个实例 `rst` 文档'


- 为标题添加索引
.. code-block:: python
    >>> from meli import format
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

- 命令行支持
.. code-block:: bash
    $ python -m meli "我是中文nihao呀"
    我是中文 nihao 呀

    $ python -m meli "我是中文nihao呀" -s code
    我是中文 `nihao` 呀

    $ # -f 指定文件路径
    $ python -m meli -f .\tests\testfile.md
    摘要算法就是通过摘要函数 f() 对任意长度的数据 data 计算出固定长度的摘要 digest，目的是为了发现原始数据是否被人篡改过。

    $ # -o 指定输出文件路径
    $ python -m meli -f .\tests\testfile.md -o testfile.md


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
