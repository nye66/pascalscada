#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把"两位选择开关"的两幅 SVG（手柄在左 / 手柄在右）合并成一幅
==============================================================
用途:
  用 THMIFlowVectorControl 只加载一幅 SVG，靠 THMIVectorFlowZone 的
  指令切换手柄位置。两幅图除了手柄和箭头外完全一样，所以合并的规则是:

    - 取左位图的公共部分（背板、开关座、倒角）
    - 把左/右手柄各自包进一个组: Handle_Left / Handle_Right
    - 箭头也放进各自的组里: Arrow_Left / Arrow_Right
    - 两套渐变改名为 SVGID_4L_ / SVGID_4R_，避免 id 撞车
    - 默认左位显示、右位隐藏 (display="none")

  合并后，状态里写:
    Handle_Left.visible=1
    Handle_Right.visible=0
  另一状态反过来即可。

用法:
  python merge_switch_svg.py "Selector switch 1 (left).svg" \
                             "Selector switch 1 (right).svg" \
                             "Selector switch 1 (two positions).svg"
"""
import re
import sys


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def cut(svg, start_id, end_id=None):
    """取出从 <g id="start_id"> 到其后第一个 </g> 之间的内容（不含外层 <g>）"""
    m = re.search(r'<g id="%s">(.*?)</g>' % re.escape(start_id), svg, re.S)
    if not m:
        raise SystemExit('没有找到组 %s' % start_id)
    return m.group(1)


def extract_handle(svg, grad_id):
    """返回 (渐变元素, 手柄 path 元素)"""
    m = re.search(r'(<linearGradient id="%s".*?</linearGradient>)' % re.escape(grad_id), svg, re.S)
    if not m:
        raise SystemExit('没有找到渐变 %s' % grad_id)
    grad = m.group(1)
    m = re.search(r'(<path fill="url\(#%s\)"[^>]*/>)' % re.escape(grad_id), svg, re.S)
    if not m:
        raise SystemExit('没有找到引用渐变 %s 的手柄路径' % grad_id)
    path = m.group(1)
    return grad, path


def extract_arrow(svg):
    body = cut(svg, 'Group_Arrow')
    m = re.search(r'(<path\b[^>]*/>)', body, re.S)
    if not m:
        raise SystemExit('没有找到箭头路径')
    return m.group(1)


def ind(text, n=1):
    pad = '\t' * n
    return '\n'.join(pad + line for line in text.strip().splitlines())


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(1)
    left_p, right_p = sys.argv[1], sys.argv[2]
    out_p = sys.argv[3] if len(sys.argv) > 3 else 'switch_two_positions.svg'

    left, right = read(left_p), read(right_p)

    # 公共部分：从头到 <g id="Group_Selector_Switch">
    head = left[:left.index('<g id="Group_Selector_Switch">')]
    tail = '</svg>'

    # Group_Selector_Switch 里除了手柄/箭头还有面板等公共内容，必须保留。
    # Group_Selector_Switch also carries common content (the face plate) that
    # must survive the merge.
    sel = cut(left, 'Group_Selector_Switch')
    sel = re.sub(r'<g id="Group_Handle">.*?</g>\s*', '', sel, flags=re.S)
    sel = re.sub(r'<g id="Group_Arrow">.*?</g>\s*', '', sel, flags=re.S)
    sel = sel.strip()

    gl, pl = extract_handle(left, 'SVGID_4_')
    gr, pr = extract_handle(right, 'SVGID_4_')
    al, ar = extract_arrow(left), extract_arrow(right)

    # 渐变改名，手柄路径跟着改引用
    gl = gl.replace('SVGID_4_', 'SVGID_4L_')
    gr = gr.replace('SVGID_4_', 'SVGID_4R_')
    pl = pl.replace('SVGID_4_', 'SVGID_4L_')
    pr = pr.replace('SVGID_4_', 'SVGID_4R_')

    def group(gid, grad, path, arrow, hidden):
        vis = ' style="display:none"' if hidden else ''
        return ('<g id="%s"%s>\n%s\n%s\n<g id="%s">\n%s\n</g>\n</g>'
                % (gid, vis, ind(grad), ind(path),
                   gid.replace('Handle', 'Arrow'), ind(arrow)))

    body = '\n'.join([
        '<g id="Group_Selector_Switch">',
        ind(sel),
        ind(group('Handle_Left', gl, pl, al, False)),
        ind(group('Handle_Right', gr, pr, ar, True)),
        '</g>',
    ])

    out = head + body + tail
    with open(out_p, 'w', encoding='utf-8') as f:
        f.write(out)
    print('written', out_p, len(out), 'bytes')
    print('组: Handle_Left / Arrow_Left (显示), Handle_Right / Arrow_Right (隐藏)')


if __name__ == '__main__':
    main()
