import os
import re
from pathlib import Path


class Formatter(object):
    def __init__(self,
                 content,
                 style=None,
                 output=None,
                 py_prompt='shell',
                 newline_between_headers=False,
                 reindex_headers=True):
        self.content = content
        self.style = style
        self.output = output
        self.py_prompt = py_prompt
        self.newline_between_headers = newline_between_headers
        self.reindex_headers = reindex_headers
        self.links = {}
        self.new_lines = []
        self.table_started = False
        self.code_block_started = False
        self.code_quote = '`'
        self.header_formatter = HeaderFormatter(self.new_lines)
        self.desc_started = False

        if self.style != 'code':
            self.code_quote = ''

        if self.py_prompt == 'shell':
            self.set_py_prompt = self.set_py_prompt_shell
        elif self.py_prompt == 'ipython':
            self.set_py_prompt = self.set_py_prompt_ipython
        else:
            raise ValueError('unknown py_prompt')

    def format(self):
        if self.new_lines:
            return self.output_result()

        if hasattr(self.content, 'read'):
            self.content = self.content.read()

        raw_lines = self.content.splitlines()

        for index, line in enumerate(raw_lines):

            if self.is_in_code_block(line):
                line = self.set_py_prompt(line)
                self.new_lines.append(line)
                continue

            if line.isspace() or not line:
                if self.new_lines and self.new_lines[-1].startswith('>'):
                    self.new_lines.append('\n')
                continue

            if self.desc_started:
                self.new_lines.append(line)
                continue

            if self.is_split(line):
                self.new_lines.append(line)

                if not index:
                    self.desc_started = True

                elif self.desc_started:
                    self.desc_started = False

                continue

            is_header = self.is_header(line)

            if is_header and self.new_lines and not self.is_header(self.new_lines[-1]):
                if self.newline_between_headers:
                    self.new_lines.append('\n<br/>\n')

            if '|' in line:
                if not self.table_started:
                    try:
                        next_line = raw_lines[index + 1]
                    except IndexError:
                        next_line = ''

                    if re.match(r'^-+?|-+?', next_line):
                        self.table_started = True

            elif self.table_started:
                self.table_started = False

            if is_header:
                self.header_formatter.add_header()

            if self.table_started:
                self.new_lines.append(line)
            else:
                self.new_lines.append(self.format_line(line))

        if self.reindex_headers:
            self.header_formatter.set()

        return self.output_result()

    def output_result(self):
        new_text = '\n'.join(self.new_lines)

        if self.output is None:
            return new_text

        if self.output == 'stream':
            return print(new_text)

        with Path(self.output).open('w', encoding='utf-8') as f:
            f.write(new_text)

    def is_header(self, line):
        return re.match(r'^#+?\s', line)

    def is_split(self, line):
        """判断该行是否为分割符"""
        return line.startswith('--') and '|' not in line

    def is_in_code_block(self, line):
        """判断是否处在代码块中"""
        if not line.strip().startswith('```'):
            return self.code_block_started

        if not self.code_block_started:
            self.code_block_started = True
        else:
            self.code_block_started = False

        return True

    def set_py_prompt_shell(self, line):
        """将 python 的提示符设置为 shell 的风格
        ex: ">>> print(\n)"
        """
        line = re.sub(r'^In \[\d+\]: ', '>>> ', line)
        line = re.sub(r'^Out\[\d+\]: ', '', line)
        line = re.sub(r'^\s*\.\.\.: ', '... ', line)
        return line

    def set_py_prompt_ipython(self, line):
        """将 python 的提示符设置为 ipython 的风格
        ex:
            [in 1] print(\n)
            [out1]

        """
        return line

    def format_line(self, line):
        return LineFormatter(line, self.code_quote).format()


class LineFormatter(object):

    def __init__(self, line, code_quote):
        self.line = line
        self.code_quote = code_quote
        self.index = 0
        self.new_words = []
        self.half_quoted = False
        self.quote_start_index = None
        self.links = {}

    def next_non_blank_word(self):
        """获取下一个非空白字符和索引"""
        next_index = self.index + 1
        next_word = ''
        while next_index < len(self.line):
            next_word = self.line[next_index]
            if not next_word.isspace():
                break
            next_index += 1
        return next_word, next_index

    def prev_non_blank_word(self):
        """获取前一个非空白字符和索引"""
        pre_index = self.index - 1
        pre_word = ''
        while pre_index >= 0:
            pre_word = self.line[pre_index]
            if not pre_word.isspace():
                break
            pre_index -= 1
        return pre_word, pre_index

    def is_bold_quote(self):
        word = self.word
        if word != '*':
            return False

        n_word, n_index = self.next_non_blank_word()
        if n_word == word and n_index == self.index + 1:
            return True

        p_word, p_index = self.prev_non_blank_word()
        return p_word == word and p_index == self.index - 1

    def add_word(self, word=None):
        if word is None:
            word = self.word
        self.new_words.append(word)

    def format(self):
        self.remove_links()

        while self.index < len(self.line):
            index_before_process = self.index

            self.process()

            if self.index == index_before_process:
                self.index += 1

        line = ''.join(self.new_words)
        return self.recover_links(line)

    def process(self):
        word = self.word

        if not self.require_space(word):
            return self.add_word()

        if not self.index or all(w.isspace() for w in self.new_words):
            # 第一个非空白字符
            if word in '#-' or word.isdigit():
                self.add_word()

            elif self.is_bold_quote():
                return self.add_word(word)

            else:
                self.add_quote()
                self.add_word(word)

        elif self.half_quoted:
            # 下一个非空白字符
            next_word, next_index = self.next_non_blank_word()
            blank_exists = next_index > self.index + 1

            if not next_word:
                self.add_word(word)
                self.add_quote()
                return

            if self.require_space(next_word):
                self.add_word(word)

            else:
                self.add_word(word)
                self.add_quote()

                if not blank_exists and not self.is_zh_mark(next_word):
                    self.add_word(' ')

        elif self.is_bold_quote():
            self.add_word()

        else:
            # 根据前后字符处理
            # 前一个字符
            prev_word, prev_index = self.prev_non_blank_word()
            prev_blank_exists = prev_index + 1 < self.index

            # 下一个非空白字符
            next_word, next_index = self.next_non_blank_word()
            blank_exists = next_index > self.index + 1

            if self.is_zh(prev_word):
                if self.is_en_mark(word) and (not next_word or self.is_zh(next_word)):
                    return self.add_word(word)

                if not self.is_zh_mark(prev_word) and not prev_blank_exists:
                    self.add_word(' ')

                self.add_quote()
                self.add_word(word)

                if self.is_zh(next_word):
                    self.add_quote()
                    if not self.is_zh_mark(next_word) and not blank_exists:
                        self.add_word(' ')

                return

            # 如果前面字符不需要处理，看后面的字符
            if self.is_zh(next_word) and not self.is_zh_mark(next_word):
                self.add_word(word)
                if not blank_exists:
                    self.add_word(' ')
                return

            self.add_word(word)

    @property
    def word(self):
        return self.line[self.index]

    def add_quote(self):
        if self.word == self.code_quote:
            return

        self.add_word(self.code_quote)
        if not self.half_quoted:
            self.half_quoted = True
            self.quote_start_index = self.index
        else:
            self.half_quoted = False
            self.quote_start_index = None

    def require_space(self, string):
        """判断字符是否为需要添加空白的字符"""
        return self.is_en(string) or self.is_en_mark(string) or string in ['-', '`', '=', '.', ',']

    def is_zh(self, string):
        """判断字符是否为中文字符"""
        return string and ('\u4e00' <= string <= '\u9fa5' or self.is_zh_mark(string))

    def is_zh_mark(self, string):
        """判断字符是否为中文标点符号"""
        return string in '，。（）：、'

    def is_mark(self, string):
        return string and (self.is_zh_mark(string) or self.is_en_mark(string))

    def is_en(self, string):
        return re.match(r'[a-zA-Z0-9_\\\[\]\{\}\*\'&#\$\(\)]', string)

    def is_en_mark(self, string):
        return string in ("'", '"', ':', ';', '(', ')', '/')

    def remove_links(self):
        """移除内容中的链接"""
        line = self.line
        links = re.findall(r'!?\[.*?\]\(.*?\)', line)

        for index, link in enumerate(set(links)):
            placeholder = ' <LinkStashed(num=%s)> ' % index
            line = line.replace(link, placeholder)
            self.links[link] = placeholder

        self.line = line

    def recover_links(self, line):
        for link, placeholder in self.links.items():
            line = line.replace(placeholder, link)
        return line


class HeaderFormatter(object):

    def __init__(self, lines):
        self.lines = lines
        self.headers = []
        self.current_index = []
        self.max_level = None

    def add_header(self, index=None):
        if index is None:
            index = len(self.lines)
        self.headers.append(index)

    def set(self):
        if not self.headers:
            return

        self.current_index = [0]

        levels = {}

        for index in self.headers:
            level = self.get_level(index)
            levels[index] = level

        self.top_level = min(level for level in levels.values())

        for index, level in levels.items():
            header_index = self.get_index(level)
            self.set_index(index, header_index)

    def get_level(self, index):
        return len(self.lines[index].split(maxsplit=1)[0])

    def get_index(self, level):
        missing = level - self.top_level
        if not missing:
            self.current_index = [self.current_index[0] + 1]
            return self.make_index(self.current_index[0])

        require_len = missing + 1

        if len(self.current_index) < require_len:
            for _ in range(require_len - len(self.current_index)):
                self.current_index.append(0)

        self.current_index[missing] += 1
        return self.make_index(self.current_index[:require_len])

    def make_index(self, index):
        if isinstance(index, int):
            return str(index)

        return '.'.join(str(i) for i in index)

    def set_index(self, line_index, header_index):
        line = self.lines[line_index]
        prefix, line = line.split(maxsplit=1)
        line = self.remove_exists_index(line)
        line = f'{prefix} {header_index}. {line}'
        self.lines[line_index] = line

    def remove_exists_index(self, line):
        if re.match(r'^\d[\d\.]+\.\s', line):
            return line.split(maxsplit=1)[-1]
        return line


def format(*args, **kwargs):
    return Formatter(*args, **kwargs).format()


def format_file(filepath, **kwargs):
    _, name = os.path.split(filepath)
    kwargs.setdefault('output', name)

    with open(filepath, 'r', encoding='utf-8') as f:
        return format(f, **kwargs)
