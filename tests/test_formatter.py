from textwrap import dedent
from unittest import TestCase

from prettymd.formatter import format


class TestFormatter(TestCase):

    def assert_formatted(self, text, expect, **kwargs):
        kwargs.setdefault('style', 'code')
        self.assertEqual(expect, format(text, output=None, **kwargs))

    def test_en_with_mark_formatted(self):
        text = '默认的表名是appName modelName，在'
        expect = '默认的表名是 `appName modelName`，在'
        self.assert_formatted(text, expect)

    def test_code_block_beautify(self):
        text = """\t```python
            def fn():

                pass
            \t```"""

        self.assert_formatted(text, text)

    def test_quote_en_words(self):
        text = '摘要算法就是通过摘要函数f()对任意长度的数据data计算出固定长度的摘要digest，目的是为了发现原始数据是否被人篡改过。'
        expect = '摘要算法就是通过摘要函数 `f()` 对任意长度的数据 `data` 计算出固定长度的摘要 `digest`，目的是为了发现原始数据是否被人篡改过。'

        self.assert_formatted(text, expect)

    def test_en_words_on_start(self):
        text = 'SHA1的结果是160 bit字节'
        expect = '`SHA1` 的结果是 `160 bit` 字节'
        self.assert_formatted(text, expect)

        text = '# 1'
        self.assert_formatted(text, text, reindex_headers=False)

    def test_table_should_not_be_beautified(self):
        text = """
        name    | password
        --------|----------
        michael | 123456
        """

        text = dedent(text).strip()
        self.assert_formatted(text, text)

    def test_link_be_ignored(self):
        text = """
        1. [codecs --- 编解码器注册和相关基类 — Python 3.12.4 文档](https://docs.python.org/zh-cn/3/library/codecs.html)
        """
        text = dedent(text).strip()
        self.assert_formatted(text, text)

    def test_word_after_number_will_be_formatted(self):
        text = '1. echo将字符串"dev"通过管道符传递给标准输出，-n选项可以去掉多余的换行符'
        expect = '1. echo 将字符串 `"dev"` 通过管道符传递给标准输出，`-n` 选项可以去掉多余的换行符'

        self.assert_formatted(text, expect)

    def test_en_word_in_zh_mark(self):
        text = "由于结果中同时也包含了文件名（在本例中文件名为-），通过指定分割符-d' '将输出拆分为两列"
        expect = "由于结果中同时也包含了文件名（在本例中文件名为 `-`），通过指定分割符 `-d' '` 将输出拆分为两列"
        self.assert_formatted(text, expect)

        text = "可以使用md5sum、sha224sum、sha1sum 等"
        expect = "可以使用 `md5sum`、`sha224sum`、`sha1sum` 等"
        self.assert_formatted(text, expect)

    def test_quote_has_blank(self):
        text = "在常规`models`操作中，某些对于关联表的查询稍有不慎可能导致产生多次查询，如:"
        expect = "在常规 `models` 操作中，某些对于关联表的查询稍有不慎可能导致产生多次查询，如:"
        self.assert_formatted(text, expect)

    def test_code_has_expr_in_quotes(self):
        text = "上面这种查询操作会造成不必要的多次查询，因为当`userlist = models.User.objects.all()`执行时"
        expect = "上面这种查询操作会造成不必要的多次查询，因为当 `userlist = models.User.objects.all()` 执行时"
        self.assert_formatted(text, expect)

    def test_parenthesis_are_ignored(self):
        text = "次查询(即JOIN查询)，"
        expect = "次查询(即 `JOIN` 查询)，"
        self.assert_formatted(text, expect)

    def test_multiple_en_formatted(self):
        text = 'MASTER 和 BINARY 是同义词'
        expect = '`MASTER` 和 `BINARY` 是同义词'
        self.assert_formatted(text, expect)

    def test_endswith_en_formatted(self):
        text = '#### 关闭 mysql 主从，关闭 binlog'
        expect = '#### 关闭 `mysql` 主从，关闭 `binlog`'
        self.assert_formatted(text, expect, reindex_headers=False)

    def test_no_br_in_headers(self):
        text = """
        ## h2
        ### h3
        """

        expect = """
        ## h2
        ### h3
        """

        self.assert_formatted(dedent(text), dedent(expect).strip(), reindex_headers=False)

    def test_br_between_in_headers(self):
        text = """
        你好
        ## h2
        ### h3
        """

        expect = """
        你好

        <br/>

        ## h2
        ### h3
        """

        self.assert_formatted(dedent(text), dedent(expect).strip(), reindex_headers=False, newline_between_headers=True)

    def test_code_with_slash(self):
        text = "使用 `git reset --hard`或 `git checkout -t -f remote/branch`"
        expect = "使用 `git reset --hard` 或 `git checkout -t -f remote/branch`"
        self.assert_formatted(text, expect)

    def test_bold_text(self):
        text = "**1. `Django`的`QuerySet`是惰性的。**`Django`的`QuerySet`对应"
        expect = "**1. `Django` 的 `QuerySet` 是惰性的。**`Django` 的 `QuerySet` 对应"
        self.assert_formatted(text, expect)

    def test_parenthesis_is_quoted(self):
        text = "默认值为 (80, 24)，如果"
        expect = "默认值为 `(80, 24)`，如果"
        self.assert_formatted(text, expect)

    def test_title_reformat(self):
        text = """
        ## h2
        ### h3
        ## h22
        #### h4
        ### h23
        """

        expect = """
        ## 1. h2
        ### 1.1. h3
        ## 2. h22
        #### 2.0.1. h4
        ### 2.1. h23
        """

        self.assert_formatted(dedent(text), dedent(expect).strip(), reindex_headers=True)

    def test_param_in_url_not_separate(self):
        url = "`https://example.com?app=1`"
        self.assert_formatted(url, url)

    def test_double_star_before_text_not_separate(self):
        text = "**创建第一个快捷方式**"
        self.assert_formatted(text, text)

    def test_no_format_for_description_zone(self):
        text = """---
        layout: post
        title: "在 django 中使用 sse"
        date: 2024-08-28 18:18 +0800
        categories: [python, django]
        tags: [django]
        ---"""
        self.assert_formatted(dedent(text), dedent(text).strip())
