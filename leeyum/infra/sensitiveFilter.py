
__all__ = ('SENSITIVE_FILTER',)


class SensitiveFilter(object):

    def __init__(self):
        self.sensitive_chains = {}
        self.delimit = '\x00'
        with open('leeyum/infra/sensitive_word.txt', encoding='utf-8') as f:
            for sensitive in f:
                self.add(sensitive.strip())

    # 将敏感词放入sensitive_chains中
    def add(self, sensitive):
        sensitive = sensitive.lower()
        chars = sensitive.strip()
        if not chars:
            return
        level = self.sensitive_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def filter(self, content, repl='*'):
        content = content.lower()
        start = 0
        ret = []
        while start < len(content):
            level = self.sensitive_chains
            step_ins = 0
            for char in content[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(content[start])
                    break
            else:
                ret.append(content[start])
            start += 1
        ret = ''.join(ret)
        if '*' in ret:
            return False, ret
        else:
            return True, ret


SENSITIVE_FILTER = SensitiveFilter()
if __name__ == "__main__":
    sf = SensitiveFilter()
    content = "测试"
    result = sf.filter(content)
    print(result)
