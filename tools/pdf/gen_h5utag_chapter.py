# -*- coding: utf-8 -*-
"""
生成《PascalSCADA 中文使用手册》新增章节: 第 20 章 汇川 H5U 标签通讯（12939）

页面规格与原手册一致:
  A4 595.32 x 841.92, 版心左 68.1 / 右 525.4, 正文 10.6pt 宋体, 章标题 16pt,
  节标题 13.6pt 黑体, 页脚居中页码 9pt。

用法: python gen_h5utag_chapter.py <输出 pdf 路径> [起始页码]
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
    t = Table([[pre]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F6F7F9')),
        ('BOX', (0, 0), (-1, -1), 0.45, GRID),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return [t, Spacer(1, 8)]


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
    def __init__(self, filename, first_page_no=115):
        BaseDocTemplate.__init__(self, filename, pagesize=A4,
                                 leftMargin=LEFT, rightMargin=RIGHT,
                                 topMargin=PAGE_H - TOP, bottomMargin=BOTTOM,
                                 title='PascalSCADA 中文使用手册',
                                 author='PascalSCADA 中文手册',
                                 subject='第 20 章 汇川 H5U 标签通讯（12939）')
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


def build(path, first_page_no=115):
    doc = ManualDoc(path, first_page_no)
    S = []

    # ============================================================ 章标题
    S.append(P('第 20 章　汇川 H5U 标签通讯（12939）', st_chap))
    S.append(P('20.1　简介', st_sec))
    S.append(P('TH5UTagTCPDriver 是汇川 H5U 系列 PLC 的<b>标签通讯</b>驱动，'
               'TCP 端口 12939。它和第 19 章的 TInovanceTCPDriver 解决的是两件事：'
               '第 19 章走 502 端口的 Modbus，标签里写 M100、D200 这类软元件；'
               '本章走 12939 端口的汇川私有监控协议，标签里写的是 AutoShop 工程里'
               '声明的<b>符号变量</b>（变量区，地址形如 UB 21004E0 / UW 21004F0）。'))
    S.append(P('需要这个驱动的原因很简单：H5U 的 Modbus 从站只开放 M/B/S/X/Y/D/R 软元件，'
               '地址最大 65535；而用 AutoShop 写的程序里，变量默认住在"变量区"，'
               '地址远超这个范围，从 Modbus 根本访问不到。触摸屏、IT7000、'
               '第三方组态软件要读写这些变量，走的都是 12939 这一路。'
               '本章的驱动就是给 PascalSCADA 补上这条路。'))
    S.append(P('驱动的结构与前面几个驱动一致：TH5UTagDriver 负责标签登记、扫描、'
               '分块与读写队列，TH5UTagTCPDriver 只负责把请求翻译成字节、把应答翻译回数值。'
               '两个单元不需要手工引用其他第三方库，纯 Pascal 实现。'))
    S += NOTE('本章的帧布局是按官方公开的端口与地址格式推断的，尚缺真实 PLC 的确认。'
              '20.8 节给出了两条标定办法：用附带的小工具探一次，或抓一份 12939 的包。'
              '标定只改 EncodePkg/DecodePkg 里几十行，标签引擎、地址换算、扫描调度都不动。'
              '现场第一次接线时请先按 20.8 节走一遍再投入运行。')

    # ============================================================ 20.2
    S.append(P('20.2　变量区与 Modbus 软元件的区别', st_sec))
    S.append(P('H5U 里一块数据放在哪，决定了用哪个驱动。表 20-1 是两条路的对照。'
               '判断方法：打开 AutoShop 的变量表，看"地址"那一列——'
               '以 UB/UW 开头的是变量区，用本章的驱动；'
               '写的是 M、D、X、Y 这些字母加十进制数字的是软元件，用第 19 章的驱动。'))
    S += TBL([
        ['', '第 19 章（TInovanceTCPDriver）', '本章（TH5UTagTCPDriver）'],
        ['端口', '502', '12939'],
        ['线上协议', '标准 Modbus TCP', '汇川私有监控协议'],
        ['地址形式', 'M100、D200、X10（软元件 + 十进制）', 'UB 21004E0、UW 21004F0（十六进制）'],
        ['地址空间', '软元件各自的小范围，最大 65535', '统一地址空间，最大 $04C4B400'],
        ['对应 PLC 侧', '软元件（M/D/X/Y/S/B/R）', '变量区（AutoShop 里声明的符号变量）'],
        ['是否需 PLC 改程序', '变量必须先映射/搬运到软元件', '不需要，变量原地读写'],
        ['文档完备度', '官方有完整编址表', '无公开文档，需按 20.8 标定'],
    ], [96, 176, 185], '表 20-1　两条通讯路线的对照')

    # ============================================================ 20.3
    S.append(P('20.3　所需组件', st_sec))
    S += TBL([
        ['对象', '属性', '填什么'],
        ['通信端口\nTTCP_UDPPort', 'Host', 'PLC 的 IP，例如 192.168.1.30'],
        ['', 'Port', '<b>12939</b>（注意不是 502）'],
        ['', 'PortType', 'ptTCP'],
        ['协议驱动\nTH5UTagTCPDriver', 'CommunicationPort', '指向上面那个 TTCP_UDPPort'],
        ['', 'FrameFormat', 'hffMbapExt（默认）/ hffHzExt，见 20.5、20.8'],
        ['', 'TraceFile', '留空表示不记录；填文件名可把每帧收发写成十六进制日志'],
        ['', 'WordAddressInBits', '默认 True，地址按 CSV 原值；见 20.6'],
        ['标签\n（TPLCTagNumber 等）', 'PLCStation', '站号，一般都填 1'],
        ['', 'MemReadFunction / MemWriteFunction', 'H5UTAG_FUNC_UB（位）/ H5UTAG_FUNC_UW（字）'],
        ['', 'MemAddress', 'CSV 地址列里 UB/UW 后面的十六进制值'],
        ['', 'RefreshTime', '刷新周期，毫秒。默认 1000，调试时可设 200'],
    ], [140, 152, 165], '表 20-2　一个最小可用的对象组合')
    S.append(P('代码里需要引用下面这些单元。四个驱动单元名容易混，注意区分：'
               'H5UTagDriver 是基类，H5UTagTCP 才是能放在窗体上的组件。'))
    S += CODE('''uses
  tcp_udpport, Tag, H5UTagTCP, H5UTagDriver, PLCTagNumber, ProtocolTypes;''')
    S.append(P('组件在 pascalscada.lpk 里编译，出现在组件面板的 Protocols 页，'
               '名字是 TH5UTagTCPDriver，图标是一个紫色的 TAG 标签。'))
    S += NOTE('FrameFormat 和 WordAddressInBits 都必须在把标签挂上驱动<b>之前</b>设好。'
              '地址换算和帧布局在标签登记、第一帧发出的那一刻就固定下来了，'
              '运行中改属性不会让已登记的标签重新换算。')

    # ============================================================ 20.4
    S.append(P('20.4　从 AutoShop 导入变量表', st_sec))
    S.append(P('变量区地址不是给人数出来的，是 AutoShop 生成的。官方的用法本来就是'
               '"PLC 侧导出变量表 → HMI 侧导入 CSV"——这份 CSV 就是给 HMI 标签通讯用的，'
               'PascalSCADA 这边照单全收。手工抄几十上百个十六进制地址既慢又容易错，'
               '所以附带一个导入工具 tools/autoshop_import.py，'
               '把 AutoShop 导出的变量表直接转成 PascalSCADA 的标签代码。'))
    S.append(NUM(1, '<b>在 AutoShop 里导出变量表。</b>打开工程的 HMI 部分，'
                   '在变量表/监视变量页面选择"导出"，保存为 CSV。'
                   '文件是 GBK 编码，前若干行以 # 开头的注释是导出信息，不用管。'))
    S.append(NUM(2, '<b>跑导入工具。</b>命令如下，第二个参数可以省略，'
                   '省略时用输入文件名做前缀。'))
    S += CODE('''python autoshop_import.py "D:\\HMI\\触摸屏变量.csv"

生成  D:\\HMI\\触摸屏变量_变量表.csv   变量清单，UTF-8，可直接用 Excel 打开
生成  D:\\HMI\\触摸屏变量_tags.txt     Pascal 代码，粘贴到窗体里即可''')
    S.append(NUM(3, '<b>核对变量清单。</b>清单有 8 列：变量名、类型、软元件、'
                   '十六进制地址、十进制地址、刷新周期、注释。类型和软元件对不上的行'
                   '（例如 Bool 却给了 UW）工具会跳过并在命令行提示。'))
    S.append(NUM(4, '<b>粘贴生成的代码。</b>_tags.txt 里是一个完整的独立过程'
                   '<font name="SimSun">AddAutoShopTags(AOwner, ADriver)</font>，'
                   '它<b>不是</b>放进 OnCreate 的语句，而是粘到窗体单元的'
                   '<font name="SimSun">implementation</font> 区'
                   '（implementation 关键字之后、文件末尾 end. 之前），'
                   '然后在窗体的 OnCreate 事件里调用它一次：'))
    S += CODE('''// 1) 窗体单元的 uses 里确保有这些单元：
uses
  ..., tcp_udpport, ProtocolDriver, Tag, H5UTagTCP, H5UTagDriver,
      PLCTagNumber, ProtocolTypes;

// 2) _tags.txt 的整个内容粘贴到 implementation 区（end. 之前）
procedure AddAutoShopTags(AOwner: TComponent; ADriver: TProtocolDriver);
var
  t: TPLCTagNumber;
  function NewTag(...): TPLCTagNumber; ...
begin
  t := NewTag('AutoModeSelect', H5UTAG_FUNC_UB, $21004E0, pttDefault, 100);
  t := NewTag('Jog_Forward',    H5UTAG_FUNC_UB, $21004E1, pttDefault, 100);
  // ...共 66 个标签...
end;

// 3) 在窗体的 OnCreate 里调用一次，第二个参数填窗体上的驱动组件名
procedure TForm1.FormCreate(Sender: TObject);
begin
  AddAutoShopTags(Self, H5UTagTCPDriver1);
end;''')
    S.append(NUM(5, '<b>编译运行。</b>变量名里的中文和点号在生成代码时已转成合法标识符'
                   '（点号变下划线，非 ASCII 字符逐字节转义），原名和注释留在行尾，'
                   '日后对照变量表不用再翻 CSV。'))
    S += NOTE('导入工具只生成标签，不生成通信对象。窗体上仍要放一个 TTCP_UDPPort 和'
              '一个 TH5UTagTCPDriver，把端口、IP、FrameFormat 设好。'
              '标签数量多时（几百个以上）建议调大 WordMaxBlockSize，减少帧数，见 20.5。')

    # ============================================================ 20.5
    S.append(P('20.5　驱动属性', st_sec))
    S += TBL([
        ['属性', '默认值', '说明'],
        ['FrameFormat', 'hffMbapExt', '帧布局。hffMbapExt 是 MBAP 头 + 32 位地址；'
                                      'hffHzExt 是 48 5A 头 + 32 位地址。见 20.8'],
        ['TraceFile', '（空）', '填文件名后，每一帧收发都按十六进制追加到该文件，'
                                '用于和抓包对照'],
        ['WordAddressInBits', 'True', 'True：UW 标签的 MemAddress 就是 CSV 里的原值；'
                                      'False：驱动把 MemAddress 除以 16 再上线路'],
        ['ReadSomethingAlways', 'True', '没有标签需要刷新时也发一帧保活，防止连接被 PLC 断开'],
        ['BitMaxHole', '50', '位区（UB）两个标签之间允许的最大空洞，超过就拆成两帧'],
        ['WordMaxHole', '10', '字区（UW）两个标签之间允许的最大空洞'],
        ['BitMaxBlockSize', '1920', '位区一帧最多读多少个位'],
        ['WordMaxBlockSize', '120', '字区一帧最多读多少个字'],
    ], [118, 62, 277], '表 20-3　TH5UTagTCPDriver 的属性')
    S.append(P('BitMaxHole / WordMaxHole 是"凑块"的松紧度：空洞小，一次请求能带更多标签，'
               '但会读到没用的地址；空洞大，帧数变多。120 个字的块上限是按 Modbus 的'
               '常规上限取的，如果现场发现 PLC 拒收长帧，先把这个值降到 60 试试。'))
    S.append(P('TraceFile 是最省事的排错手段：设成 D:\\h5u_trace.txt，跑十秒钟，'
               '打开文件就能看到每一帧的十六进制收发。和 Wireshark 的抓包对比，'
               '哪一字节不对一眼就能看出来。'))

    # ============================================================ 20.6
    S.append(P('20.6　标签地址与数据宽度', st_sec))
    S.append(P('标签的地址由两个属性拼成：MemReadFunction 说"哪个区"，'
               'MemAddress 说"区里第几个"。表 20-4 是两个区的编号。'))
    S += TBL([
        ['区', 'MemReadFunction', '常量名', '地址含义', '访问'],
        ['变量区位地址', '1', 'H5UTAG_FUNC_UB', 'CSV 里 UB 后面的十六进制值', '按位读写'],
        ['变量区字地址', '17', 'H5UTAG_FUNC_UW', 'CSV 里 UW 后面的十六进制值', '按字读写'],
    ], [96, 92, 122, 150, 74], '表 20-4　两个区的编号')
    S.append(P('MemAddress 是 Cardinal，最大 $04C4B400。填的时候有两种写法，等价：'))
    S += CODE('''Tag.MemAddress := $21004F0;   // 十六进制字面量，推荐，和 CSV 一致
Tag.MemAddress := 34604272;   // 同一个值的十进制''')
    S.append(P('WordAddressInBits 默认 True，意思是"MemAddress 就是 CSV 里那个值"，'
               '驱动不再换算。只有当你的地址是从别处拿到的、以字为单位（比如自己数出来'
               '的第几个字）时才设为 False，让驱动乘以 16 再上线路。'
               '两种写法混用时最容易出错，建议全工程统一用 True + CSV 原值。'))
    S.append(P('数据类型靠 TagType 决定，与地址无关。表 20-5 是 AutoShop 类型到 TagType 的对应，'
               '导入工具已经按这张表生成好了。'))
    S += TBL([
        ['AutoShop 类型', 'TagType', '占几个字', '说明'],
        ['Bool', 'pttDefault', '—', '位区标签，MemReadFunction 用 H5UTAG_FUNC_UB'],
        ['Int16 / UInt16', 'pttSmallInt / pttWord', '1', '字区标签，有符号/无符号'],
        ['Int32 / UInt32', 'pttLongInt / pttDWord', '2', '低字在前的两个字'],
        ['Float', 'pttFloat', '2', 'IEEE754 单精度，低字在前'],
        ['Double', 'pttDouble', '4', '双精度，一般少用'],
    ], [120, 118, 72, 147], '表 20-5　AutoShop 类型与 TagType 的对应')
    S += NOTE('32 位和浮点标签占两个连续的字，地址必须是 AutoShop 分配的起始地址，'
              '不要自己往前挪一个字。数组变量（CSV 里"数量"列大于 1）要用 TPLCBlock 整体读，'
              '或者按元素地址拆成多个标签——导入工具目前按单元素生成，数组请手工处理。')

    # ============================================================ 20.7
    S.append(P('20.7　分步示例', st_sec))
    S.append(NUM(1, '<b>确认 12939 端口通。</b>先在 PLC 上电、网线接好的情况下'
                   '用 AutoShop 在线监视一次，能监视就说明端口是开的。'
                   'AutoShop 监视用的正是 12939。'))
    S.append(NUM(2, '<b>放组件。</b>窗体上放 TTCP_UDPPort（Host 填 PLC 的 IP，'
                   'Port 填 12939，PortType 选 ptTCP）和 TH5UTagTCPDriver，'
                   '把驱动的 CommunicationPort 指向端口组件。'))
    S.append(NUM(3, '<b>标定帧格式。</b>先按 20.8 节跑一次探测工具，'
                   '确认 FrameFormat 该选哪一个。这一步不做，后面很可能一直是超时。'))
    S.append(NUM(4, '<b>建标签。</b>用 20.4 的导入工具生成代码，粘进窗体 OnCreate。'))
    S.append(NUM(5, '<b>接线与启动。</b>标签的 PLCStation 填 1，RefreshTime 先设 200 便于观察，'
                   '把驱动的 Active 置 True。'))
    S.append(P('一个完整的最小工程长这样：'))
    S += CODE('''unit Unit1;
{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, Forms, Controls,
  tcp_udpport, Tag, H5UTagTCP, H5UTagDriver, PLCTagNumber, ProtocolTypes;

type
  TForm1 = class(TForm)
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
  private
    FPort: TTCP_UDPPort;
    FDriver: TH5UTagTCPDriver;
    FMode: TPLCTagNumber;
    FCount: TPLCTagNumber;
  end;

var
  Form1: TForm1;

implementation''')
    S.append(P('先建端口和驱动，再逐个建标签。每建一个标签，把它的 ProtocolDriver 指向驱动：'))
    S += CODE('''procedure TForm1.FormCreate(Sender: TObject);
begin
  FPort := TTCP_UDPPort.Create(Self);
  FPort.Host := '192.168.1.30';
  FPort.Port := 12939;
  FPort.PortType := ptTCP;

  FDriver := TH5UTagTCPDriver.Create(Self);
  FDriver.CommunicationPort := FPort;
  FDriver.FrameFormat := hffMbapExt;   // 按 20.8 标定结果改
  FDriver.TraceFile := 'D:\\h5u_trace.txt';

  FMode := TPLCTagNumber.Create(Self);
  FMode.Name := 'AutoModeSelect';
  FMode.PLCStation := 1;
  FMode.MemReadFunction := H5UTAG_FUNC_UB;
  FMode.MemWriteFunction := H5UTAG_FUNC_UB;
  FMode.MemAddress := $21004E0;
  FMode.TagType := pttDefault;
  FMode.RefreshTime := 200;
  FMode.ProtocolDriver := FDriver;

  FCount := TPLCTagNumber.Create(Self);
  FCount.Name := 'ProductCount';
  FCount.PLCStation := 1;
  FCount.MemReadFunction := H5UTAG_FUNC_UW;
  FCount.MemWriteFunction := H5UTAG_FUNC_UW;
  FCount.MemAddress := $21004F0;
  FCount.TagType := pttSmallInt;
  FCount.RefreshTime := 200;
  FCount.ProtocolDriver := FDriver;

  FDriver.Active := True;
end;

procedure TForm1.FormDestroy(Sender: TObject);
begin
  FDriver.Active := False;
end;

end.''')
    S.append(P('注意标签是先设属性、最后才赋 ProtocolDriver——赋值的那一刻标签就去驱动登记地址了，'
               '属性没设全就登记，读到的是空地址。'))

    # ============================================================ 20.8
    S.append(P('20.8　标定帧格式（上线前必做）', st_sec))
    S.append(P('汇川没有公开 12939 的报文格式，官方《IT7000 通信指南》只到配置界面这一层：'
               '确认了协议名叫 H5U TCP Monitor Protocol、端口必须设 12939、'
               '站号 1、读/写一次最多 120 个字、超时 180ms、请求间隔 5ms，'
               '以及"PLC 侧导出变量表 → HMI 侧导入 CSV"的用法——'
               '这份 CSV 正是 20.4 导入工具吃的那个文件。但报文本身长什么样，'
               '官方一个字没提。驱动里实现了两种候选布局，参数是 FrameFormat：'))
    S += TBL([
        ['FrameFormat', '帧结构（请求）', '适用推测'],
        ['hffMbapExt', '事务号(2) 协议(2) 长度(2) 站号(1) 功能码(1) '
                       '地址(4) 数量(2)', '报文以 MBAP 为底、地址扩到 32 位'],
        ['hffHzExt', '48 5A 序号(2) 保留(4) 长度(2) 功能码(1) 地址(4) 数量(2)',
         '汇川自有的 48 5A 帧头'],
    ], [92, 258, 107], '表 20-6　两种候选帧布局')
    S.append(P('哪一个是真的，只有 PLC 说了算。两种办法，任选其一。'))
    S.append(P('<b>办法一：用探测工具打一枪。</b>tools/h5u_tag_probe.py 会按上面两种布局'
               '（外加几种微调）各发一条"读 2 个字"的请求，把 PLC 的真实应答打印出来。'
               '它只发只读请求，不会改动 PLC 里的任何数据。'))
    S += CODE('''python h5u_tag_probe.py 192.168.1.30
python h5u_tag_probe.py 192.168.1.30 --addr 21004F0 --unit 1

输出里出现 "RX ..." 且有功能码回显的那一行，就是正确的布局，
把它对应的名字填进 FrameFormat。全部超时说明 IP/端口/网线有问题，
先确认 AutoShop 在线监视能连上。''')
    S.append(P('<b>办法二：抓一份包。</b>让 AutoShop 在线监视（或让汇川触摸屏）'
               '对着 PLC 跑十几秒，同时用 Wireshark 过滤 tcp.port == 12939，'
               '存成 pcap。按下面的顺序读这份包：'))
    S.append(NUM(1, '找第一条"客户端 → PLC"的报文，看开头两个字节：'
                   '是 48 5A 就走 hffHzExt，否则看第三、四字节是不是 00 00（协议号），'
                   '是就走 hffMbapExt。'))
    S.append(NUM(2, '确认功能码。读位、读字、写单个、写多个分别是哪几个功能码，'
                   '和 Modbus 的 01/03/06/16 对不对得上。'))
    S.append(NUM(3, '确认地址宽度。地址是 4 字节还是 2 字节，高位在前还是后。'))
    S.append(NUM(4, '确认应答的数据区。位数据是打包成字节还是每个位一字节，'
                   '字数据的高低字节顺序。'))
    S.append(P('把结论（或者直接那份 pcap）发出来，改驱动的 EncodePkg / DecodePkg 即可。'
               '需要动的只有这两个函数里构造帧头、写地址、解析应答那几十行；'
               '标签登记、地址换算、分块、扫描调度都在基类里，一行不用改。'))
    S += NOTE('驱动的两种布局不是"随便猜两个"，而是按已知线索收敛出来的：'
              '功能码沿用了 Modbus 的 01/03/05/06/15/16（触摸屏厂商的驱动文档里'
              '读位写位都对应这几个码），地址按 32 位大端（因为变量区地址超过 16 位），'
              '帧头取 MBAP 与 48 5A 两种最常见的形态。真机上先试 hffMbapExt，不通再换 hffHzExt。')

    # ============================================================ 20.9
    S.append(P('20.9　常见问题', st_sec))
    S += TBL([
        ['现象', '原因', '处理'],
        ['连不上，端口拒绝', '12939 未开或走错端口', '确认用的是 12939 不是 502；'
                                                   '用 AutoShop 在线监视验证'],
        ['连上但全部超时', '帧布局不对', '按 20.8 标定，换 FrameFormat'],
        ['应答来了但值全是 0', '地址没有乘 16 / 多乘了 16',
         'WordAddressInBits 用默认 True，MemAddress 填 CSV 原值'],
        ['Bool 读成乱码数字', 'MemReadFunction 填成了字区',
         'Bool 变量用 H5UTAG_FUNC_UB'],
        ['写不进去', 'MemWriteFunction 没填或与读不一致',
         '读写两个属性填同一个区编号'],
        ['32 位数高低颠倒', '字序问题', '低字在前，见 20.6 表 20-5'],
        ['变量改名后读不到', '地址随工程重编译变了',
         '重新导出 CSV、重跑导入工具'],
        ['几百个标签刷新很慢', '块太小、帧太多', '调大 WordMaxBlockSize，'
                                            '或在 PLC 侧把相关变量排在一起'],
    ], [130, 148, 179], '表 20-7　常见问题')

    # ============================================================ 20.10
    S.append(P('20.10　协议参考', st_sec))
    S.append(P('请求帧由 TH5UTagTCPDriver.EncodePkg 构造，应答由 DecodePkg 解析，'
               '两者都按 FrameFormat 分支。核心参数：功能码读位 1、读字 3、'
               '写单个位 5、写单个字 6、写多个位 15、写多个字 16；'
               '地址 32 位大端；数量 16 位大端；写多值请求在数量后跟一个字节的字节数'
               '和值本身（位区按位打包，字区每字两字节）。'))
    S.append(P('读取时一帧最多 1920 位或 120 字，超过就由基类自动拆成多帧，'
               '标签数量再多也不会撞上单帧上限。没有标签需要刷新时，'
               'ReadSomethingAlways 会让驱动定期发一帧保活，避免 PLC 主动断开空闲连接。'
               '异常应答（功能码最高位置 1）会按 Modbus 的异常码翻译成 TProtocolIOResult，'
               '含义与表 18-8 一致。'))
    S.append(P('单元构成：H5UTagTCP（帧编解码、事务号、残帧处理）与 H5UTagDriver'
               '（两个区的内存管理、地址换算、分块扫描、读写队列）。'
               '地址常量 H5UTAG_FUNC_UB / H5UTAG_FUNC_UW 与表 20-4 一一对应，'
               '扩展新区域时同步修改 H5UTAG_DEV_FUNC、H5UTAG_DEV_NAME、H5UTAG_DEV_ISBIT'
               '三张表即可。'))
    S.append(P('自测脚本 tools/h5utagtest.lpr 共 45 项，覆盖两个区的地址换算、'
               '两种帧布局的编码、正常与异常应答的解码、残帧、剩余字节计算、'
               'SizeOfTag 与地址字面量。改动驱动后跑一遍即可回归，'
               '编译命令与第 19 章相同。'))

    doc.build(S)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'h5utag_chapter.pdf'
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 115
    build(out, start)
    print('written', out)
