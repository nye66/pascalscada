# -*- coding: utf-8 -*-
"""
把一个 PNG 图标编码成 Lazarus .lrs 资源格式并追加到 pascalscada.lrs。

用法: python make_lrs_icon.py <图标.png> <组件类名> [目标.lrs]
"""
import sys, re

def encode_pascal_bytes(data: bytes) -> str:
    """按 FPC 字符串常量规则编码: 可打印 ASCII 用 'lit', 其余用 #NNN"""
    out = []
    lit = []
    for b in data:
        if 32 <= b <= 126 and b != 39:          # 39 = '
            lit.append(chr(b))
        else:
            if lit:
                out.append("'" + ''.join(lit).replace("'", "''") + "'")
                lit = []
            out.append('#%d' % b)
    if lit:
        out.append("'" + ''.join(lit).replace("'", "''") + "'")
    return ''.join(out)

def wrap_tokens(tokens: str, first_indent='  ', cont_indent='  +', width=72) -> str:
    """把整串 token 按行折行, 续行以 + 开头, 不把 token 拆开"""
    lines, cur = [], ''
    first = True
    i = 0
    while i < len(tokens):
        # 找下一个完整 token 结束位置
        j = i
        if tokens[i] == '#':
            while j < len(tokens) and tokens[j].isdigit():
                j += 1
        else:  # 'lit'
            j = tokens.index("'", i + 1)
            while True:
                j = tokens.index("'", j + 1)
                if j + 1 < len(tokens) and tokens[j + 1] == "'":
                    j += 2
                    continue
                break
            j += 1
        tok = tokens[i:j]
        indent = first_indent if first else cont_indent
        if cur and len(cur) + len(tok) > width:
            lines.append(cur)
            cur = cont_indent + tok
            first = False
        else:
            cur = cur + tok if cur else indent + tok
        i = j
    if cur:
        lines.append(cur)
    return '\n'.join(lines)

def main():
    png_path, cls = sys.argv[1], sys.argv[2]
    target = sys.argv[3] if len(sys.argv) > 3 else \
        r"E:/Pascalscada/pascalscada_v0-master/pascalscada.lrs"
    data = open(png_path, 'rb').read()

    src = open(target, encoding='latin-1').read()
    if "LazarusResources.Add('%s'" % cls in src:
        print('SKIP: %s 已存在于 %s' % (cls, target))
        return

    tokens = encode_pascal_bytes(data)
    block = "LazarusResources.Add('%s','PNG',[\n%s\n]);\n" % (
        cls, wrap_tokens(tokens))
    with open(target, 'a', encoding='latin-1', newline='') as f:
        if not src.endswith('\n'):
            f.write('\n')
        f.write(block)
    print('APPENDED %s (%d bytes png) -> %s' % (cls, len(data), target))

if __name__ == '__main__':
    main()
