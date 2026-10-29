# -*- coding: utf-8 -*-
"""
生成《PascalSCADA 中文使用手册》新增章节: 第 17 章 罗克韦尔 Logix PLC（EtherNet/IP）

页面规格与原手册一致:
  A4 595.32 x 841.92, 版心左 68.1 / 右 525.4, 正文 10.6pt 宋体, 章标题 16pt,
  节标题 13.6pt 黑体, 页脚居中页码 9pt。

用法: python gen_lgx_chapter.py <输出 pdf 路径> [起始页码]
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
    pre = XPreformatted(text.strip('\n'), st_code)
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
    def __init__(self, filename, first_page_no=94):
        BaseDocTemplate.__init__(self, filename, pagesize=A4,
                                 leftMargin=LEFT, rightMargin=RIGHT,
                                 topMargin=PAGE_H - TOP, bottomMargin=BOTTOM,
                                 title='PascalSCADA 中文使用手册',
                                 author='PascalSCADA 中文手册',
                                 subject='第 17 章 罗克韦尔 Logix PLC（EtherNet/IP）')
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


def build(path, first_page_no=94):
    doc = ManualDoc(path, first_page_no)
    S = []

    # ============================================================ 章标题
    S.append(P('第 17 章　罗克韦尔 Logix PLC（EtherNet/IP）', st_chap))
    S.append(P('17.1　简介', st_sec))
    S.append(P('TLGXDriver 是罗克韦尔（Rockwell / Allen-Bradley）CompactLogix、ControlLogix、'
               'GuardLogix 等 Logix 系列控制器的驱动，走 EtherNet/IP 的显式报文（CIP），'
               'TCP 端口 44818。名字里的 LGX 是 Logix 的缩写，与 LG 产电（现 LS 产电）的 PLC '
               '没有任何关系——那家公司的 PLC 在 PascalSCADA 里没有专用驱动，一般用 Modbus TCP 接。'))
    S.append(P('它和前面几章的驱动有一个根本区别：没有寄存器地址，也没有站号。Logix 用符号寻址，'
               'Studio 5000 里给变量起的名字就是地址，报文里直接带这个名字（tag path），由控制器'
               '自己去找对应的内存。所以配置一个标签时，填的不是 D100、4x00001 这类数字地址，'
               '而是 Tank1_Level、Recipe[3]、Program:MainProgram.Counter 这样的名字。'))
    S.append(P('第二个区别是长度：CIP 单帧上限 490 字节，驱动会把多个标签合并进一个"多服务包"'
               '（Multiple Service Packet，服务码 0x0A）里一次读回。标签越多、越集中，合并越充分，'
               '扫描周期就越短；一个标签一帧的写法在这里会被放大成几十倍的报文量。'))
    S.append(P('适用范围：控制器自带以太网口（或装了 EN2T/EN3T 模块）并且固件支持符号访问。'
               '老的 SLC 500 / MicroLogix 走的是 DF1 或 CIP 的 PCCC 对象，本驱动不支持；'
               '那种机型请用第 12 章的 S7 之外的方案另找网关，或者直接用 Modbus 网关转一道。'))
    S += NOTE('本章与第 16 章信捷驱动同为后补章节，排在手册末尾，前面的章节编号与目录页码不受影响。'
              '标签、扫描、块这些通用概念见第 4 章；同样是"报文里带地址"的思路，可以对照第 7 章的三菱驱动看。')

    # ============================================================ 17.2
    S.append(P('17.2　所需组件', st_sec))
    S.append(P('三个对象就够：端口负责收发字节，驱动负责 CIP 会话和标签管理，标签代表控制器里的'
               '一个变量。与寄存器型驱动相比，标签这一层要填的属性少得多——没有功能码，也没有站号。'))
    S += TBL([
        ['对象', '属性', '填什么'],
        ['通信端口\nTTCP_UDPPort', 'Host', '控制器的 IP，例如 192.168.1.10'],
        ['', 'Port', '44818。该组件默认是 102，必须改'],
        ['', 'PortType', 'ptTCP'],
        ['', 'ExclusiveDevice', '保持默认 False。置 True 后设计期不会真正连接，'
                                'Tag Builder 就读不到标签列表（见 17.7）'],
        ['协议驱动\nTLGXDriver', 'CommunicationPort', '指向上面那个 TTCP_UDPPort'],
        ['', 'ReadOnly', '默认 False；只监视不控制时置 True'],
        ['标签\n（TPLCTagNumber 等）', 'LongAddress', '符号路径，例如 Tank1_Level、Tank1.Level'],
        ['', 'TagType', '与控制器里的数据类型对应，见表 17-3'],
        ['', 'RefreshTime', '刷新周期，毫秒。默认 1000，调试时可设 200'],
    ], [124, 100, 233], '表 17-1　一个最小可用的对象组合')
    S.append(P('在代码里创建这些对象需要引用下面的单元：'))
    S += CODE('''uses
  tcp_udpport, LGXDriver, PLCTagNumber, ProtocolTypes;''')
    S.append(P('驱动单元 LGXDriver 编译在 pascalscada.lpk 里，类显示在组件面板的 Protocols 页；'
               'Tag Builder 向导在 pascalscada_dsng 包里（单元 rockwelltagassistant、'
               'ulgxtagbuilder），只在设计期存在，运行期不需要。'))

    # ============================================================ 17.3
    S.append(P('17.3　准备 PLC', st_sec))
    S.append(P('Logix 的调试问题大多不在驱动上，而在控制器的变量属性上。上电前按下面五条检查一遍。'))
    S.append(NUM(1, '<b>网段要对。</b>控制器默认可能还是 192.168.1.x 或 BOOTP 没配置的状态。'
                   '用 Studio 5000 的 Who Active 或 BOOTP-DHCP Tool 确认 IP，再把上位机网卡设到同一网段。'))
    S.append(NUM(2, '<b>变量要在控制器域，或者写全路径。</b>Studio 5000 的变量分控制器域（Controller Tags）'
                   '和程序域（Program Tags）。控制器域的变量直接填名字；程序域的必须写成 '
                   'Program:程序名.变量名，例如 Program:MainProgram.Counter。漏了前缀，控制器会回'
                   '"对象不存在"（0x05）。'))
    S.append(NUM(3, '<b>外部访问权限要给够。</b>变量属性里的 External Access 决定 CIP 能不能读、能不能写。'
                   '设为 None 或 Read Only 时，读可能成功而写一直失败；设为 Read/Write 才能写。'
                   '这一项在变量属性的下拉框里改，改完要下载。'))
    S.append(NUM(4, '<b>名字要合法。</b>不能有空格和中文；不能和内置类型重名（BOOL、DINT 之类）；'
                   '数组下标从 0 开始（梯形图里的 Recipe[1] 是第二个元素）。名字的大小写在驱动里'
                   '不敏感，但拼错一个字母就是"对象不存在"。'))
    S.append(NUM(5, '<b>先验端口。</b>命令行执行 telnet 192.168.1.10 44818'
                   '（Windows 10/11 需先在"启用或关闭 Windows 功能"里装 Telnet 客户端）。'
                   '窗口清空并出现光标说明端口通；提示失败就先查网段、网线和防火墙，不要怀疑驱动。'))
    S += NOTE('控制器能同时接的 CIP 连接数有限（CompactLogix 通常 32 个左右，HMI、变频器、'
              '另一台上位机都在抢）。调试时先断开 Studio 5000 的在线连接和其它上位机，'
              '否则会出现"能连上、过一会儿掉线"或干脆连不上。')

    # ============================================================ 17.4
    S.append(P('17.4　驱动属性', st_sec))
    S.append(P('TLGXDriver 只公开了两个属性，比寄存器型驱动少得多。它没有 MaxBlockSize、MaxHole 这类'
               '调参项——分帧完全由 CIP 的 490 字节上限和多标签合并逻辑决定，不对外暴露。'))
    S += TBL([
        ['属性', '默认值', '说明'],
        ['ReadOnly', 'False', '置 True 后不再发送任何写请求，写操作立即返回成功但不会落到控制器。'
                              '只监视的画面建议打开。'],
        ['ReadSomethingAlways', 'True', '每个扫描周期至少读一个标签。关掉后，端口未激活或所有标签'
                                       '都还没到期时驱动会空转，CPU 占用略低，故障发现变慢。'],
    ], [136, 62, 259], '表 17-2　TLGXDriver 的可调属性')
    S.append(P('除了这两个属性，驱动还提供几个方法，主要在 Tag Builder 和有特殊需求的场景里用：'))
    S += TBL([
        ['方法', '作用'],
        ['TagListLoaded', '本端口对应的控制器标签列表是否已经完整读过一遍'],
        ['BrowseTagList(out List; ForceReload)', '在线读取控制器的标签列表（控制器域、程序域、'
                                                 'UDT 成员、数组元素），同步阻塞，读的时候界面会停住'],
        ['ClearTagListCache', '丢弃缓存的标签列表，下次访问重新读'],
    ], [186, 271], '表 17-3　TLGXDriver 的公开方法')

    # ============================================================ 17.5
    S.append(P('17.5　符号寻址', st_sec))
    S.append(P('标签的 LongAddress 填的就是 Studio 5000 里的变量名，需要带上访问路径的部分：'
               '成员用点号分隔，数组用方括号给下标（从 0 开始），程序域变量前面加 Program:程序名.。'
               '驱动的地址校验就按这几条规则做的，写错了标签不会进入扫描。'))
    S += TBL([
        ['LongAddress', '指向的对象'],
        ['Motor1_Run', '控制器域的单个变量（BOOL、DINT、REAL 等）'],
        ['Tank1.Level', 'UDT（结构体）里的一个成员，名字是成员名'],
        ['Recipe[3]', '一维数组的第 4 个元素（下标 0 起）'],
        ['Recipe[2,1]', '二维数组的第二行第三列'],
        ['Recipe[0].Level', '数组元素里的成员'],
        ['Program:MainProgram.Counter', 'MainProgram 这个程序里的变量'],
        ['Line1.Tank[2].Level', '嵌套结构：结构体里的数组元素再取成员'],
        ['Logix_String.DATA', 'STRING 结构里的字符数据（STRING 的用法见 17.6）'],
    ], [214, 243], '表 17-4　LongAddress 的写法')
    S.append(P('几条要记住的约束：名字里不能有空格；方括号里只能放数字，不能放变量；'
               '大小写不敏感（驱动统一转成小写再比对），但字符必须一致。'
               '如果变量是在程序域里、且程序名不叫 MainProgram，前缀要换成实际的程序名。'))
    S += CODE('''tag.LongAddress := 'Tank1.Level';
tag.LongAddress := 'Recipe[3]';
tag.LongAddress := 'Program:MainProgram.Counter';''')
    S += NOTE('一个标签只能指向一个变量或一个成员，没有"从某个地址开始读一片"的写法。'
              '要读整片数组，用 TPLCBlock 并把它指向数组首元素（例如 Recipe），Size 填元素个数，'
              '详见 17.8 的示例。')

    # ============================================================ 17.6
    S.append(P('17.6　数据类型对照', st_sec))
    S.append(P('TagType 要根据控制器里变量的真实类型填。填错不会报错——驱动照样按字节读回来，'
               '只是按另一种类型解释，结果就成了乱码级的大数或者极小的浮点数。'))
    S += TBL([
        ['控制器里的类型', 'TagType', '字节', '说明'],
        ['BOOL', 'pttByte', '1', '驱动把非 0 转成 1，写非 0 即为置位'],
        ['SINT', 'pttShortInt', '1', '8 位有符号'],
        ['INT', 'pttSmallInt', '2', '16 位有符号'],
        ['DINT', 'pttLongInt', '4', '32 位有符号，最常用'],
        ['LINT', 'pttInt64', '8', '64 位有符号'],
        ['USINT', 'pttByte', '1', '8 位无符号'],
        ['UINT', 'pttWord', '2', '16 位无符号'],
        ['UDINT、DWORD', 'pttDWord', '4', '32 位无符号'],
        ['ULINT', 'pttQWord', '8', '64 位无符号'],
        ['REAL', 'pttFloat', '4', '单精度浮点，IEEE 格式'],
        ['LREAL', 'pttDouble', '8', '双精度浮点'],
        ['STRING', '（用 TPLCString）', '88', '结构体，见下面说明'],
        ['UDT（自定义结构）', '（逐成员读）', '—', '没有整个结构对应的标签类型'],
    ], [116, 116, 46, 179], '表 17-5　Logix 数据类型与 TagType 的对应')
    S.append(P('Logix 的 STRING 其实是一个结构：LEN 是 DINT，DATA 是 SINT[82]，加上填充共 88 字节。'
               '驱动目前没有实现 Logix 专用的字符串格式，所以要用 TPLCString 把 LongAddress 指到 '
               'DATA 成员上，并把 StringType 设成 stC：'))
    S += CODE('''str.LongAddress := 'MyString.DATA';
str.StringType  := stC;
str.StringSize  := 81;''')
    S.append(P('UDT 也是一样：没有"整个结构一个标签"的写法，要按成员逐个建标签，LongAddress 写成 '
               'Tank1.Level 这种路径。成员很多时，用 17.7 的 Tag Builder 一次导入比手工建省事得多。'))
    S += NOTE('数组里的 BOOL 在 Logix 里是打包存放的（32 个位折成一个 DWORD），驱动不解包，'
              '所以 BOOL 数组既不能整块读，也不能逐个下标读。需要位数组时，在控制器里改成 '
              'SINT 数组，或改用 DINT 的位操作自己拆分。')

    # ============================================================ 17.7
    S.append(P('17.7　Tag Builder（标签导入向导）', st_sec))
    S.append(P('手工敲几十个变量名既费时又容易错，设计期可以用向导把控制器的标签列表直接读上来。'
               '做法是：把端口和驱动放好，<b>把端口的 Active 设成 True</b>（设计期也要设，否则读不到），'
               '然后在驱动上点右键，选 Tag Builder。'))
    S.append(P('向导打开后会先读一次标签列表，界面会停住几秒（读列表是同步的，标签越多越久）。'
               '读完之后可以用名字过滤、按种类过滤，勾选"显示数组元素""显示结构体成员""显示程序域变量"，'
               '再按全选、反选挑选要导入的项，最后设一个扫描周期和名字前缀，点"导入"。'))
    S.append(P('导入时按标签的种类自动建对象，省掉了手工配属性这一步：'))
    S += TBL([
        ['控制器里的对象', '导入成什么', '怎么配的'],
        ['简单变量（DINT、REAL、BOOL…）', 'TPLCTagNumber', 'TagType 按类型对应，Size = 1'],
        ['数组（Recipe[10]）', 'TPLCBlock', 'TagType 用元素类型，Size = 元素个数'],
        ['STRING', 'TPLCString', 'StringType = stC，LongAddress 指向 .DATA，'
                                 'StringSize = DATA 大小 - 1'],
        ['UDT 的成员', 'TPLCTagNumber', '逐个导入，LongAddress 是对应的成员路径'],
    ], [148, 108, 201], '表 17-6　Tag Builder 导入规则')
    S.append(P('向导有意跳过三类对象：<b>BOOL 数组</b>（打包位，驱动不解包，导进来读到的值一定是错的）、'
               '<b>整个 UDT</b>（没有对应的标签类型，成员会被单独列出）、<b>控制器内部类型</b>'
               '（带系统标志的保留类型，不是用户变量）。跳过时向导会提示数量，不用管。'))
    S += NOTE('设计期能连上控制器，前提是 TTCP_UDPPort 的 ExclusiveDevice 为 False。'
              '置 True 之后，端口在设计期不会真正建立连接（ReallyActive 直接返回 False），'
              '向导会提示端口未激活、读不到任何东西。要到现场连真机、又不想让 IDE 占着连接，'
              '才把它置 True。')

    # ============================================================ 17.8
    S.append(P('17.8　分步示例', st_sec))
    S.append(P('下面做一个最小工程：一个启动位、一个液位浮点、一片配方数组、一个程序域计数器。'
               '控制器 IP 假定 192.168.1.10，变量名与 Studio 5000 里一致。'))
    S.append(P('<b>步骤 1：放端口。</b>窗体上放一个 TTCP_UDPPort，Name 改成 TCPPort；Host 填 '
               '192.168.1.10，Port 改成 44818，PortType 保持 ptTCP，ExclusiveDevice 保持 False。'))
    S.append(P('<b>步骤 2：放驱动。</b>再放一个 TLGXDriver，Name 改成 Logix，把 CommunicationPort '
               '指向 TCPPort，ReadOnly 保持 False。'))
    S.append(P('<b>步骤 3：建标签。</b>按下表填，注意第三个是 TPLCBlock（整片数组），不是 TPLCTagNumber。'))
    S += TBL([
        ['Name（控件类）', '关键属性', '访问的对象'],
        ['Logix_Motor1_Run\n（TPLCTagNumber）',
         'LongAddress Motor1_Run；TagType pttByte；RefreshTime 200', 'BOOL 变量'],
        ['Logix_Tank_Level\n（TPLCTagNumber）',
         'LongAddress Tank1.Level；TagType pttFloat', 'UDT 里的 REAL 成员'],
        ['Logix_Recipe\n（TPLCBlock）',
         'LongAddress Recipe；TagType pttLongInt；Size 10', 'DINT[10] 整片数组'],
        ['Logix_Counter\n（TPLCTagNumber）',
         'LongAddress Program:MainProgram.Counter；TagType pttLongInt', '程序域 DINT'],
    ], [104, 235, 118], '表 17-7　示例工程的四个标签')
    S.append(P('<b>步骤 4：启动。</b>把 TCPPort.Active 设成 True。驱动先去 RegisterSession，再 '
               'Forward Open 建连接，然后开始按 RefreshTime 扫描。四个标签会被合并进一个多服务包，'
               '一轮扫描只发一帧。'))
    S.append(P('<b>步骤 5：验证。</b>在控制器里让 Motor1_Run 每 500 ms 翻转一次，画面上放一个 '
               'THMILed 绑上去，灯闪说明整条链路通了；再看 Tank1.Level 的 Value 是否与 Studio 5000 '
               '在线监视的值一致，一致说明类型和路径都没错。'))
    S.append(P('同样的对象写成代码是这样：'))
    S += CODE('''var
  TCPPort: TTCP_UDPPort;
  Logix: TLGXDriver;
  tagBit, tagCounter: TPLCTagNumber;
  blk: TPLCBlock;
begin
  TCPPort := TTCP_UDPPort.Create(Self);
  TCPPort.Host := '192.168.1.10';
  TCPPort.Port := 44818;
  TCPPort.PortType := ptTCP;
  TCPPort.ExclusiveDevice := False;

  Logix := TLGXDriver.Create(Self);
  Logix.CommunicationPort := TCPPort;

  tagBit := TPLCTagNumber.Create(Self);
  tagBit.Name := 'Logix_Motor1_Run';
  tagBit.LongAddress := 'Motor1_Run';
  tagBit.TagType := pttByte;

  blk := TPLCBlock.Create(Self);
  blk.Name := 'Logix_Recipe';
  blk.LongAddress := 'Recipe';
  blk.TagType := pttLongInt;
  blk.Size := 10;

  tagBit.ProtocolDriver := Logix;
  blk.ProtocolDriver   := Logix;

  TCPPort.Active := True;
end;''')
    S.append(P('注意 ProtocolDriver 是最后赋的：驱动在登记标签的那一刻就要读到 LongAddress，'
               '先连驱动后填地址会让标签用空地址注册一次，得多做一次注销和重挂。向导生成的代码'
               '也是按这个顺序写的，原因相同。'))

    # ============================================================ 17.9
    S.append(P('17.9　常见问题', st_sec))
    S.append(P('Logix 驱动的报错很有指向性，按下面的对应关系基本能直接定位。'))
    S += TBL([
        ['现象', '原因', '处理'],
        ['全部标签 ioObjectNotExists（05）',
         '变量名拼错；程序域变量漏了 Program:程序名. 前缀',
         '用 Studio 5000 复制变量名；确认前缀与程序名一致'],
        ['个别标签 ioObjectNotExists',
         '变量被删了、改名了，或者只存在于离线工程、没有下载',
         '重新下载控制器程序后点 Tag Builder 重新导入'],
        ['ioIllegalRegAddress（04 或 26）',
         '数组下标越界；UDT 成员路径写了一半',
         '核对数组长度（下标 0 起）；把 LongAddress 补成完整路径'],
        ['全部标签 ioTimeOut', 'IP 或端口不对；防火墙；CIP 连接数被占满',
         'telnet 试 44818；断开 Studio 5000 在线和其它上位机'],
        ['读到很怪的数（浮点变成极小数）',
         'TagType 与控制器类型不一致（例如 REAL 当 DINT 读）',
         '按表 17-5 改 TagType；DINT 与 REAL 互读必然出乱码'],
        ['写入没反应但也没报错', 'ReadOnly 被置 True；变量 External Access 是只读',
         '关掉 ReadOnly；把变量属性改成 Read/Write 再下载'],
        ['BOOL 数组读不到或值全错', 'Logix 把 32 个位打包成一个 DWORD，驱动不解包',
         '在控制器里改成 SINT 数组，或按 DINT 位自己拆'],
        ['扫描周期越来越长', '标签太多太散，一帧塞不下 490 字节，被拆成很多帧',
         '关掉不用的标签；把同一数组改成 TPLCBlock；放宽 RefreshTime'],
    ], [132, 168, 157])
    S.append(Spacer(1, 2))

    # ============================================================ 17.10
    S.append(P('17.10　协议参考', st_sec))
    S.append(P('抓包核对时先看 EtherNet/IP 的封装头，固定 24 字节，后面跟命令相关的数据：'))
    S += TBL([
        ['字段', '字节', '说明'],
        ['Command', '2', '0065 注册会话、0066 注销、006F SendRRData（非连接）、'
                         '0070 SendUnitData（连接内）'],
        ['Length', '2', '命令数据区的字节数'],
        ['Session Handle', '4', 'RegisterSession 的应答里给，后续报文都要带'],
        ['Status', '4', '0 表示成功，非 0 是封装层错误'],
        ['Sender Context', '8', '发送方的标识，应答原样带回'],
        ['Options', '4', '固定 0'],
    ], [110, 48, 299], '表 17-8　EtherNet/IP 封装头')
    S.append(P('建链顺序是：先把 CIP 路径（0x91 符号段）编码进请求，用 RegisterSession 拿到会话号，'
               '再用 Forward Open（服务 0x54）建一条连接，之后读写都走 SendUnitData。'
               '读写的 CIP 服务码如下：'))
    S += TBL([
        ['服务码', '含义', '驱动里的用途'],
        ['0x4C', 'Read Tag', '一次读一个标签（不超过一帧时）'],
        ['0x4D', 'Write Tag', '写一个标签，值按类型跟在路径后面'],
        ['0x52', 'Read Tag Fragmented', '读分片：一个标签的数据超过一帧时按偏移续读'],
        ['0x53', 'Write Tag Fragmented', '写分片：同上，写入超过一帧的块'],
        ['0x0A', 'Multiple Service Packet', '一次打包读多个标签，总长不超过 490 字节'],
    ], [66, 148, 243], '表 17-9　驱动用到的 CIP 服务')
    S.append(P('控制器拒绝请求时，应答的通用状态字节按下面的对应关系转成标签的 IOResult：'))
    S += TBL([
        ['状态码', '驱动返回', '含义'],
        ['05', 'ioObjectNotExists', '对象（变量）不存在：名字错、路径不全、没下载'],
        ['04、26', 'ioIllegalRegAddress', '路径或地址不合法：数组下标越界、成员不存在'],
        ['13', 'ioIllegalRequest', '请求本身不合法：长度、类型不匹配'],
        ['FF', 'ioIllegalMemoryAddress', '内存地址非法'],
        ['FE', 'ioCommError', '通信错误：帧被截断或连接已断'],
        ['其他', 'ioUnknownError', '未归类的状态，需抓包看原始状态字节'],
    ], [66, 176, 215], '表 17-10　CIP 状态码与 TProtocolIOResult 的对应')

    # ============================================================ 17.11
    S.append(P('17.11　相关示例', st_sec))
    S.append(P('仓库里目前没有专门的 Logix 示例工程。搭法可以照 examples/laz_modbus_tcp_example 的结构改：'
               '把 TModBusTCPDriver 换成 TLGXDriver，端口 Port 改成 44818，然后按 17.8 建标签即可。'
               '块、结构体、字符串混用的写法可以看 examples/laz_isotcp_demonstration。'))
    S.append(P('驱动随 pascalscada.lpk 一起编译，单元是 LGXDriver（CIP 报文、会话、标签列表、扫描）。'
               '它不依赖罗克韦尔的任何 DLL，也不依赖 libplctag，纯 Pascal 实现，因此可以编译到 '
               'Win32/Win64/Linux 各个平台。自己写测试程序时，把 LGXDriver 加进 uses，用假的端口'
               '回放字节，就能不开控制器验证帧格式。'))
    S.append(P('Tag Builder 在 pascalscada_dsng 包里，只在设计期安装；如果右键菜单里没有 Tag Builder，'
               '说明这个设计期包没有装好——重新编译并安装 pascalscada_dsng.lpk，再重启 IDE。'))
    S.append(P('本章的表 17-5 与 LGXDriver 里的 TAG_CIP_TYPE_* 常量、LGXTypeToTagType 函数一一对应，'
               '表 17-10 与 DoRead/DoWrite 里的 case 分支一一对应。日后驱动扩展类型或状态码，'
               '改这里的两张表即可。'))

    doc.build(S)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'lgx_chapter.pdf'
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 94
    build(out, start)
    print('written', out)
