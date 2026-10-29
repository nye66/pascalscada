# -*- coding: utf-8 -*-
"""
生成《PascalSCADA 中文使用手册》新增章节: 第 21 章 矢量图形控件与 SVGChanges

页面规格与原手册一致:
  A4 595.32 x 841.92, 版心左 68.1 / 右 525.4, 正文 10.6pt 宋体, 章标题 16pt,
  节标题 13.6pt 黑体, 页脚居中页码 9pt。

用法: python gen_vector_chapter.py <输出 pdf 路径> [起始页码]
"""
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, XPreformatted)

# ---------------------------------------------------------------- 字体
pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))
pdfmetrics.registerFont(TTFont('Consolas', 'C:/Windows/Fonts/consola.ttf'))
pdfmetrics.registerFontFamily('SimSun', normal='SimSun', bold='SimHei',
                              italic='SimSun', boldItalic='SimHei')
pdfmetrics.registerFontFamily('SimHei', normal='SimHei', bold='SimHei',
                              italic='SimHei', boldItalic='SimHei')

# ---------------------------------------------------------------- 版式
PAGE_W, PAGE_H = 595.32, 841.92
LEFT, RIGHT = 68.1, 69.9
TOP, BOTTOM = 841.92 - 72.7, 62.0
CONTENT_W = PAGE_W - LEFT - RIGHT

BODY = 10.6
LEAD = 15.6

st_body = ParagraphStyle('body', fontName='SimSun', fontSize=BODY, leading=LEAD,
                         alignment=TA_JUSTIFY, firstLineIndent=21.2, spaceBefore=0,
                         spaceAfter=6, wordWrap='CJK')
st_bullet = ParagraphStyle('bullet', parent=st_body, firstLineIndent=0,
                           leftIndent=21.2, bulletIndent=6, spaceAfter=3)
st_chap = ParagraphStyle('chap', fontName='SimSun', fontSize=16, leading=19.5,
                         spaceBefore=0, spaceAfter=14, wordWrap='CJK')
st_sec = ParagraphStyle('sec', fontName='SimHei', fontSize=13.6, leading=15.5,
                        spaceBefore=15, spaceAfter=7, wordWrap='CJK')
st_cell = ParagraphStyle('cell', fontName='SimSun', fontSize=9.2, leading=12.4,
                         wordWrap='CJK')
st_cell_h = ParagraphStyle('cellh', fontName='SimHei', fontSize=9.2, leading=12.4,
                           wordWrap='CJK')
st_code = ParagraphStyle('code', fontName='Consolas', fontSize=8.4, leading=11.4)
st_note = ParagraphStyle('note', fontName='SimSun', fontSize=9.6, leading=14.0,
                         wordWrap='CJK', alignment=TA_JUSTIFY, firstLineIndent=0)
st_cap = ParagraphStyle('cap', fontName='SimHei', fontSize=9.2, leading=12.0,
                        spaceBefore=4, spaceAfter=4, wordWrap='CJK')

GRAY_HDR = colors.HexColor('#EDEFF2')
GRID = colors.HexColor('#B7BDC6')


def P(text, style=st_body):
    return Paragraph(text, style)


def NUM(n, text):
    return Paragraph(text, st_bullet, bulletText='%d.' % n)


def TBL(rows, widths, caption=None):
    data = []
    for r, row in enumerate(rows):
        line = []
        for cell in row:
            if isinstance(cell, Paragraph):
                line.append(cell)
            else:
                line.append(Paragraph(str(cell), st_cell_h if r == 0 else st_cell))
        data.append(line)
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.45, GRID),
        ('BACKGROUND', (0, 0), (-1, 0), GRAY_HDR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.2),
    ]))
    out = []
    if caption:
        out.append(Paragraph(caption, st_cap))
    out.append(t)
    out.append(Spacer(1, 8))
    return out


def CODE(text):
    # Consolas 没有中文字形：先转义 XML，再把非 ASCII 片段包上宋体
    import re
    t = text.strip('\n')
    t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    t = re.sub(r'([^\x00-\x7f]+)', r'<font name="SimSun">\1</font>', t)
    pre = XPreformatted(t, st_code)
    tbl = Table([[pre]], colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F6F7F9')),
        ('BOX', (0, 0), (-1, -1), 0.45, GRID),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return [tbl, Spacer(1, 8)]


def NOTE(text):
    body = Paragraph(text, st_note)
    t = Table([[body]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F6FA')),
        ('LINEBEFORE', (0, 0), (0, -1), 2.2, colors.HexColor('#7A9CC0')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return [Spacer(1, 2), t, Spacer(1, 9)]


class ManualDoc(BaseDocTemplate):
    def __init__(self, filename, first_page_no=123):
        BaseDocTemplate.__init__(self, filename, pagesize=A4,
                                 leftMargin=LEFT, rightMargin=RIGHT,
                                 topMargin=PAGE_H - TOP, bottomMargin=BOTTOM,
                                 title='PascalSCADA 中文使用手册',
                                 author='PascalSCADA 中文手册',
                                 subject='第 21 章 矢量图形控件与 SVGChanges')
        self.first_page_no = first_page_no
        frame = Frame(LEFT, BOTTOM, CONTENT_W, TOP - BOTTOM, id='body',
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id='page', frames=[frame],
                                            onPage=self.decorate)])

    def decorate(self, canv, doc):
        canv.saveState()
        canv.setFont('Consolas', 9)
        canv.setFillColor(colors.HexColor('#333333'))
        canv.drawCentredString(PAGE_W / 2.0, 31,
                               str(self.first_page_no + doc.page - 1))
        canv.restoreState()


def build(path, first_page_no=123):
    doc = ManualDoc(path, first_page_no)
    S = []

    # ============================================================ 章标题
    S.append(P('第 21 章　矢量图形控件与 SVGChanges', st_chap))
    S.append(P('21.1　简介', st_sec))
    S.append(P('矢量控件家族有两个：THMIBasicVectorControl 显示一幅静态 SVG'
               '（把文件内容粘进 SVGContents 属性即可）；THMIFlowVectorControl 在此之上'
               '加了"按区间改图"的能力——挂一个标签，标签值落在哪个区间，'
               '就执行哪个区间配置的一组 SVGChanges 指令，对 SVG 里的元素'
               '<b>重新着色、换成渐变、显示/隐藏，以及选择流程线的走向</b>。'
               '阀门开闭变色、选择开关左右切位、指示灯亮灭，都是它的工作。'))
    S.append(P('SVGChanges 是一套一行一条的文本指令，写在'
               'ColorAndFlowStates 集合的每个区间（THMIVectorFlowZone）里。'
               '指令的格式统一是 <font name="SimSun">元素id.属性=值</font>，'
               '元素 id 就是 SVG 文件里写的 id。本章把全部指令列成表，'
               '再用一个两位选择开关从头到尾走一遍。'))
    S += NOTE('本章内容对应 2026 年 10 月之后的版本：渐变引用（fill=url(#…)）'
              '与显示/隐藏（visible）指令是新增的，旧版本不认识这两条，'
              '升级后请重新编译 pascalscada_hmi 包。')

    # ============================================================ 21.2
    S.append(P('21.2　SVGChanges 指令总表', st_sec))
    S.append(P('一条指令 = 元素 id + 点 + 属性 + 等号 + 值。属性有六种，'
               '值的形式取决于属性，见表 21-1。解析时整行转小写，'
               '所以大小写随便写；不符合语法的行会被直接丢弃，'
               '不会报错也不会半途执行——排错时先检查有没有拼错。'))
    S += TBL([
        ['指令', '值', '作用'],
        ['id.fill=…', 'fill', '填充色用区间自己的 Color'],
        ['', 'border', '填充色用区间的 BorderColor'],
        ['', 'flow', '填充色用输入流程线的颜色'],
        ['', '#RRGGBB', '填充色用这个固定颜色'],
        ['', 'url(#渐变id)', '填充换成 SVG 里声明的渐变（21.5）'],
        ['id.border=…', '同上四种', '描边色，规则与 fill 相同'],
        ['id.stop-color=…', 'fill/border/flow/#RRGGBB',
         '改渐变色标（stop）的颜色，见 21.5'],
        ['id.stop-opacity=0～100', '整数', '改渐变色标的不透明度（百分比）'],
        ['id.visible=1/0', '1、0、true、false', '显示或隐藏元素/整组，见 21.4'],
        ['flow.output=N', '从 1 数', '让输入的流程线从第 N 个输出口出去'],
        ['flow', '（整行只有这个词）', '等价于 flow.output=1'],
    ], [128, 122, 207], '表 21-1　SVGChanges 全部指令')
    S.append(P('几个对颜色值的通用说明：fill 和 border 的值写 fill/border/flow 时，'
               '颜色不是写死的，而是取自当前区间的 Color、BorderColor'
               '或输入流程线的当前色——同一个 SVG 配上一组区间，'
               '阀门开是绿、关是红、故障是黄，改区间颜色就行，SVG 不用动。'
               '写 #RRGGBB 则是写死的颜色。'))
    S += NOTE('id 必须与 SVG 里的 id 完全对应（比较时忽略大小写）。'
              '组元素的 id 可以整组操作：对 g 写 visible 能一次显示/隐藏组里'
              '全部内容；对 g 写 fill 则只影响没有自带填充的子元素——'
              '要整组换色，请在 SVG 里让子元素继承 fill（不写 fill 属性）。')

    # ============================================================ 21.3
    S.append(P('21.3　区间与标签联动', st_sec))
    S.append(P('ColorAndFlowStates 是一个区间集合，每个区间三组属性：'
               '<b>选中条件</b>（标签值落在什么范围算命中）、<b>颜色</b>'
               '（fill/border/flow 三种取色来源的出处）、<b>SVGChanges</b>'
               '（命中后执行的指令）。控件的 PLCTag 指向标签，'
               '标签值变化时重新选区间、重画 SVG。'))
    S += TBL([
        ['属性', '说明'],
        ['ZoneType', '选中条件：ztEqual 等于、ztRange 区间内、ztBit 位等于、'
                     'ztNotEqual 不等、ztOutOfRange 区间外、ztGreaterThan 大于、'
                     'ztLessThan 小于'],
        ['Value1 / Value2', '条件用的一个或两个值；SetValues 一次设好并保持 '
                            'Value1 ≤ Value2'],
        ['IncludeV1 / IncludeV2', '边界值算不算命中'],
        ['DefaultZone', '没有区间命中时用它兜底显示'],
        ['Color', '本区间的颜色：指令值写 fill 时，SVG 元素用它着色'],
        ['BorderColor', '指令值写 border 时的取色'],
        ['Flow', '本区间是否让流程线带色流动'],
        ['SVGChanges', '命中后逐条执行的指令（表 21-1）'],
    ], [118, 339], '表 21-2　区间（THMIVectorFlowZone）的属性')
    S.append(P('控件一侧的属性：PLCTag 挂数值标签；OutputPolylineLeft/Right'
               '（或三通以上的 FlowOutputPolylines 集合）接流程线控件；'
               'InputFlowPolyline 接进线——指令里写 flow 取的颜色、'
               '以及流程走向，都以这条进线为准。'))
    S.append(P('阀门类（THMIFlowValve）、三通（THMI2OutFlowVectorControl）、'
               ' fork（THMIForkedFlowVectorControl）、升降机（THMIFlowElevator）'
               '都是同一族，区间和指令的用法完全一致，只是预设的手柄'
               '和输出口数不同。'))
    S += NOTE('控件还有一组闪烁属性：Blink 打开闪烁、BlinkColor 闪烁色、'
              'BlinkTargetID 指定闪哪个元素（写元素 id）。闪烁是在着色之后'
              '叠加的，区间的颜色仍会生效。')

    # ============================================================ 21.4
    S.append(P('21.4　实例：两位选择开关', st_sec))
    S.append(P('CAD 导出的设备图常常一个位置一幅图。以两位选择开关为例：'
               '手柄在左一幅、在右一幅，两幅文件里除手柄和箭头外完全一样。'
               '按老做法做两个控件叠在一起切 Visible，状态一多就乱；'
               '正确的做法是<b>合并成一幅 SVG，两个手柄都放在里面，'
               '用 visible 指令切换</b>。'))
    S.append(NUM(1, '<b>合并。</b>用 tools/merge_switch_svg.py 把两幅图合成一幅：'
                   '手柄各自成组（Handle_Left / Handle_Right），箭头跟进各自的组'
                   '（Arrow_Left / Arrow_Right），两套渐变改名 SVGID_4L_ / '
                   'SVGID_4R_ 避免重名，右手柄默认 display="none"。'))
    S += CODE('''python merge_switch_svg.py "Selector switch 1 (left).svg" \\
            "Selector switch 1 (right).svg" \\
            "Selector switch 1 (two positions).svg"''')
    S.append(NUM(2, '<b>加载。</b>把控件的 SVGContents 设为合并后文件的内容'
                   '（文本编辑器打开，全选复制粘贴进属性即可）。'))
    S.append(NUM(3, '<b>配区间。</b>两个区间，条件各管一个位置，'
                   'SVGChanges 互相颠倒显示：'))
    S += CODE('''区间 1（标签值 = 0，手柄在左）：
  Handle_Left.visible=1
  Handle_Right.visible=0

区间 2（标签值 = 1，手柄在右）：
  Handle_Left.visible=0
  Handle_Right.visible=1''')
    S.append(NUM(4, '<b>联动。</b>PLCTag 挂上开关量标签（0/1），'
                   '标签一变手柄立即切到另一边。想给某个位置加提示色，'
                   '在同一个区间的 SVGChanges 里再补一行着色指令，例如 '
                   '<font name="SimSun">Group_Switch_Backplate.fill=#FFE0B2</font>。'))
    S += NOTE('visible 对整组生效：组里哪怕有二十条路径，隐藏组 itself 一行就够。'
              '这也是指示灯、双色按钮一类"两个状态两幅图"的通用做法。'
              '每个区间都把两个组都写明（一显一隐），不要只写一半——'
              '区间命中时整个 SVG 会按该区间的指令重画，漏写的组保持 SVG '
              '文件里的默认状态，容易在两个区间之间来回跳时对不上。')

    # ============================================================ 21.5
    S.append(P('21.5　渐变：整体引用与改色标', st_sec))
    S.append(P('跟渐变打交道有两种需求，对应两种指令，别混用：'))
    S.append(NUM(1, '<b>把元素的填充换成某个渐变</b>——值写 url(#渐变id)。'
                   '渐变必须已经在 SVG 的 defs 里声明过（CAD 导出的图一般都有，'
                   '形如 SVGID_1_）。例如：'))
    S += CODE('''corpo.fill=url(#SVGID_3_)     // 填充换成 SVGID_3_ 渐变
corpo.border=url(#SVGID_3_)  // 描边同理''')
    S.append(P('这条指令适合"同一个件，有时纯色有时渐变"的场景——'
               '比如报警时把手柄从金属渐变换成红色实心，恢复正常再换回来。'
               '两个区间一条写 url(#…) 一条写 #RRGGBB 就完成了切换，'
               '渐变本体始终留在 SVG 里。'))
    S.append(NUM(2, '<b>渐变不变，改渐变里的颜色</b>——对渐变的 stop 元素'
                   '用 stop-color / stop-opacity。适合"同一套渐变，'
                   '正常时绿、报警时红"的场景：'))
    S += CODE('''parada1.stop-color=#00B050    ! 起始色标改绿
parada2.stop-color=#00B050    ! 结束色标也改绿
parada1.stop-opacity=80       ! 不透明度 80%''')
    S.append(P('两条路线的效果差别在于：换引用（url）是整个元素换一套渐变，'
               '渐变几何、色标数都可以不同；改色标是渐变结构不动、只换颜色，'
               '多个引用同一渐变的元素会一起变色。'))
    S += NOTE('引用名在指令里大小写不限（内部会按 SVG 里的真实 id 补正），'
              '但渐变 id 在 SVG 里必须唯一。合并两幅图时最容易踩的坑就是'
              '两幅图都有 SVGID_4_：必须先把其中一个改名（连同 fill="url(#…)" '
              '里的引用一起），否则只有一个渐变生效。merge_switch_svg.py '
              '已经处理了这一点。')

    # ============================================================ 21.6
    S.append(P('21.6　显示与缩放', st_sec))
    S.append(P('SVG 文件有两个"尺寸"：width/height 是画布声明，'
               'viewBox 是内容坐标系。CAD 导出的图常常 width="64px" 而 '
               'viewBox="0 0 112.5 109.23"——两者不一致时，'
               '缩放行为由控件的 Stretch / Proportional 决定：'))
    S += TBL([
        ['Stretch', 'Proportional', '效果'],
        ['True', 'True', '保持宽高比缩放到控件内最大，居中。推荐'],
        ['True', 'False', '拉伸铺满控件，图形随控件变形'],
        ['False', '—', '按 viewBox 的自然尺寸绘制，不放大；'
                        '旧版本此模式对 viewBox 与声明尺寸不一致的文件会裁切，'
                        '已修复为按 viewBox 完整绘制'],
    ], [62, 92, 303], '表 21-3　缩放模式')
    S.append(P('透明背景（Background=clNone）时，SVG 里没画东西的区域'
               '直接透出窗体底色。背板类图形常有斜角、圆角，'
               '透出的底色形状不规则，容易被误认为"图形被裁掉了"。'
               '怀疑裁切时，把 Background 设成一个鲜艳的颜色跑一下：'
               '控件的真实绘图区会整个变成该颜色，图形完整与否一目了然。'))
    S += NOTE('AutoCAD/Illustrator 导出时尽量让 width/height 与 viewBox '
              '等比例，并在导出选项里保留 id（AI 的"对象名"选项、'
              'Inkscape 默认保留）。id 丢了，SVGChanges 就没有作用对象了。')

    # ============================================================ 21.7
    S.append(P('21.7　常见问题', st_sec))
    S += TBL([
        ['现象', '原因', '处理'],
        ['指令写了没反应', '语法不符被丢弃',
         '对照表 21-1 检查拼写；id 与属性都用小写试一次'],
        ['切状态后图形"缺角"', 'SVG 背板本来就有斜角，透明背景透出窗体底色',
         '按 21.6 用 Background 红色验证；是形状就不是 bug'],
        ['底部/右侧被切掉一条', 'viewBox 与声明尺寸不一致且未缩放',
         'Stretch=True + Proportional=True，或升级到已修复的版本'],
        ['两个渐变只有一个生效', '两幅图合并后渐变 id 重名',
         '改名其中一个，连同 url(#…) 引用一起，见 21.5'],
        ['手柄切换后位置对不上', '区间漏写了另一半 visible',
         '每个区间把所有可切换的组都写全，见 21.4 注意'],
        ['渐变色标改了没变化', '元素引用的不是这个渐变',
         '检查 SVG 里 fill="url(#…)" 指向的渐变 id'],
        ['流程线不走选择的路', 'flow.output 的序号超出输出口数',
         '序号从 1 数；三通以上检查 FlowOutputPolylines 个数'],
    ], [132, 150, 175], '表 21-4　常见问题')

    # ============================================================ 21.8
    S.append(P('21.8　测试与示例', st_sec))
    S.append(P('指令解析与显示/隐藏/渐变切换都有自动化测试'
               '（tests/ut.vectorcontrol.pas，随 pascalscada_hmi_tests 运行），'
               '覆盖每条指令的语法校验、非法值拒收、区间命中后的实际效果。'
               '改动 hmi_draw_basic_vector_control 单元后跑一遍即可回归。'))
    S.append(P('现成示例：examples/hmi_flowvectorcontrol 是区间着色的最小演示；'
               'examples/laz_svg_example 演示 SVGContents 的加载；'
               'tools/merge_switch_svg.py 与 tools/svgswitchtest.lpr 是本章'
               '选择开关实例的合并与渲染验证工具，可直接复用到其它"多位图"。'
               '辅助诊断时，把 SVG 交给 svgswitchtest 渲染成 PNG，'
               '可以脱离控件确认"图本身长什么样"。'))

    doc.build(S)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'vector_chapter.pdf'
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 123
    build(out, start)
    print('written', out)
