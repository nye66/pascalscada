# -*- coding: utf-8 -*-
"""
生成《PascalSCADA 中文使用手册》新增章节: 第 16 章 信捷 Xinje PLC（TCP 内部协议）

页面规格与原手册一致:
  A4 595.32 x 841.92, 版心左 68.1 / 右 525.4, 正文 10.6pt 宋体, 章标题 16pt,
  节标题 13.6pt 黑体, 页脚居中页码 9pt。

用法: python gen_xinje_chapter.py <输出 pdf 路径> [起始页码]
"""
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, XPreformatted, PageBreak)

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
TOP, BOTTOM = 841.92 - 72.7, 62.0        # 版心上/下边界(距页面下边)
CONTENT_W = PAGE_W - LEFT - RIGHT        # 457.32

BODY = 10.6
LEAD = 15.6

st_body = ParagraphStyle('body', fontName='SimSun', fontSize=BODY, leading=LEAD,
                         alignment=TA_JUSTIFY, firstLineIndent=21.2, spaceBefore=0,
                         spaceAfter=6, wordWrap='CJK')
st_body_ni = ParagraphStyle('body_ni', parent=st_body, firstLineIndent=0)
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


def LI(text):
    return Paragraph(text, st_bullet, bulletText='•')


def NUM(n, text):
    return Paragraph(text, st_bullet, bulletText='%d.' % n)


def TBL(rows, widths, caption=None):
    """rows: 第一行为表头; 单元格里的字符串按普通单元格样式, 需要富文本时传 Paragraph"""
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


# ---------------------------------------------------------------- 文档模板
class ManualDoc(BaseDocTemplate):
    def __init__(self, filename, first_page_no=86):
        BaseDocTemplate.__init__(self, filename, pagesize=A4,
                                 leftMargin=LEFT, rightMargin=RIGHT,
                                 topMargin=PAGE_H - TOP, bottomMargin=BOTTOM,
                                 title='PascalSCADA 中文使用手册',
                                 author='PascalSCADA 中文手册',
                                 subject='第 16 章 信捷 Xinje PLC（TCP 内部协议）')
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


def build(path, first_page_no=86):
    doc = ManualDoc(path, first_page_no)
    S = []

    # ============================================================ 章标题
    S.append(P('第 16 章　信捷 Xinje PLC（TCP 内部协议）', st_chap))
    S.append(P('16.1　简介', st_sec))
    S.append(P('TXinJETCPDriver 是信捷（Xinje）PLC 的内部协议驱动，走 TCP/IP，端口 502。'
               '报文头沿用 Modbus TCP 的 6 个字节（事务号、协议号、长度），后面接站号、命令字、'
               '软元件数据码、24 位地址和数量——也就是把 Modbus 的功能码位置换成了信捷自己的'
               '命令字：0x1E 读位、0x1F 写位、0x20 读字、0x21 写字。'))
    S.append(P('与 Modbus 最大的区别在寻址：不需要把软元件换算成线圈或保持寄存器的分区地址，'
               '报文里直接给"软元件类型 + 编号"。所以梯形图上写 D100、M0、X10，配置里就填 100、0、10，'
               '再指定一个表示软元件类型的 MemReadFunction 即可，详见 16.5。'))
    S.append(P('驱动家族分两层，与第 7 章的三菱驱动结构相同：TXinJEDriver 负责标签注册、扫描调度、'
               '地址翻译、长块拆分和内存管理；TXinJETCPDriver 只负责把请求编成字节串、把应答解成值。'
               '因此标签怎么配、属性怎么调、出错怎么查，与三菱那一章高度相似——读过第 7 章可以直接'
               '从 16.4 往下看。'))
    S.append(P('适用范围：PLC 需要开放这个内部协议的 TCP 端口（带以太网口的 XD、XE、XL 系列机型'
               '默认开放，端口 502，具体以 XDPPro 的"以太网设置"页面为准）。如果现场是 XC 系列'
               '（或 XC 加以太网模块），通常只支持 Modbus TCP，请改用第 5 章的 TModBusTCPDriver，'
               '并按 Modbus 的地址规则配置。'))
    S += NOTE('本章是后来新增的章节，排在手册末尾，以免打乱前面各章的编号和已排好的目录页码。'
              '协议驱动的通用概念见第 4 章；另一个"报文里直接带软元件类型"的驱动见第 7 章。')

    # ============================================================ 16.2
    S.append(P('16.2　所需组件', st_sec))
    S.append(P('一个能跑的采集至少有三种对象：通信端口负责收发字节，协议驱动负责把字节翻译成值，'
               '标签代表设备里的一个存储单元。三者的关系在第 4 章 4.3 节已经画过，这里只列本驱动'
               '需要填的项。'))
    S += TBL([
        ['对象', '属性', '填什么'],
        ['通信端口\nTTCP_UDPPort', 'Host', 'PLC 的 IP，例如 192.168.6.6'],
        ['', 'Port', '502。该组件默认是 102，必须改'],
        ['', 'PortType', 'ptTCP'],
        ['', 'ExclusiveDevice', 'True。多数小型 PLC 只允许一个连接'],
        ['协议驱动\nTXinJETCPDriver', 'CommunicationPort', '指向上面那个 TTCP_UDPPort'],
        ['', 'IOAddressFormat', '默认 xiofOctal，见 16.6'],
        ['标签\n（TPLCTagNumber 等）', 'PLCStation', '站号，直连单机填 1'],
        ['', 'MemReadFunction', '软元件代码，见表 16-3、表 16-4'],
        ['', 'MemWriteFunction', '与读功能码相同（读写共用一张表）'],
        ['', 'MemAddress', '软元件编号，只填数字，不带 M、D 前缀'],
    ], [122, 98, 237], '表 16-1　一个最小可用的对象组合')
    S.append(P('在代码里创建这些对象时，需要引用下列单元：'))
    S += CODE('''uses
  tcp_udpport, XinJETCP, PLCTagNumber, ProtocolTypes;''')
    S.append(P('驱动单元 XinJEDriver、XinJETCP 已经加进 pascalscada.lpk，注册代码在 '
               'src/scada_dsng/scadareg.pas 里，类显示在组件面板的 Protocols 页。如果设计期'
               '看不到 TXinJETCPDriver，请重新打开并编译安装 pascalscada.lpk，再新建一个工程。'))

    # ============================================================ 16.3
    S.append(P('16.3　准备 PLC', st_sec))
    S.append(P('上电之前先在 PLC 侧确认几件事，能省掉后面大半的排错时间。'))
    S.append(NUM(1, '<b>确认 IP 与端口。</b>用 XDPPro 联机，打开"以太网设置"页面，记下 PLC 的 IP 地址、'
                   '子网掩码和网关，并确认协议端口为 502。'))
    S.append(NUM(2, '<b>留出连接数。</b>小型 PLC 允许的 TCP 连接数有限，XDPPro 的在线监控、触摸屏、'
                   '上位机会互相抢连接。调试上位机时先断开 XDPPro，否则可能出现"能连上但几秒就掉"'
                   '或干脆连不上的现象。'))
    S.append(NUM(3, '<b>先验端口通不通。</b>在命令行执行 telnet 192.168.6.6 502（Windows 10/11 需先在'
                   '"启用或关闭 Windows 功能"里勾选"Telnet 客户端"）。窗口清空并出现光标说明端口是通的；'
                   '提示连接失败，先查网段、网线和防火墙，不要急着怀疑驱动。'))
    S.append(NUM(4, '<b>定站号。</b>一台 PLC 直连时 PLCStation 填 1；经网关或多站网络时按现场设定填，'
                   '驱动接受 1 到 255。超出范围的标签不会进入扫描，在属性面板里会一直显示为无效。'))
    S.append(NUM(5, '<b>确认没被保护。</b>PLC 侧不需要做任何寄存器映射或地址转换表，驱动直接按软元件'
                   '访问；但写操作要求 PLC 不处于密码保护或禁止写入的状态，否则写入会返回错误码 04。'))
    S += NOTE('电脑和 PLC 不在同一网段是最常见的"连不上"原因。用 DHCP 拿到的地址常常与 PLC 的'
              '出厂网段（192.168.6.x）不一致，先把网卡改成同网段静态地址再试。')

    # ============================================================ 16.4
    S.append(P('16.4　驱动属性', st_sec))
    S.append(P('这些属性都能在 Object Inspector 里改，也可以在代码里赋值。除 IOAddressFormat，'
               '其余与第 7 章的三菱驱动同名同义。'))
    S += TBL([
        ['属性', '默认值', '说明'],
        ['ReadOnly', 'False', '置 True 后驱动不再发送任何写请求，标签的写入立即返回成功但不会'
                              '落到 PLC。适合只监视、不控制的画面。'],
        ['ReadSomethingAlways', 'True', '每个扫描周期至少读一个标签。关掉后，端口未激活或所有标签'
                                       '都还没到期时驱动会空转，CPU 占用略低，但故障发现变慢。'],
        ['BitMaxHole', '50', '两个位标签之间最多允许空多少个未声明的位，仍合并成一帧。'],
        ['WordMaxHole', '10', '同上，单位是字。'],
        ['BitMaxBlockSize', '1920', '单帧最多读/写多少个位，超过就自动拆成多帧。'],
        ['WordMaxBlockSize', '120', '单帧最多读/写多少个字，超过就自动拆成多帧。'],
        ['IOAddressFormat', 'xiofOctal', 'X、Y 的编号按八进制还是十进制解释，见 16.6。'],
    ], [120, 62, 275], '表 16-2　TXinJETCPDriver 的可调属性')
    S.append(P('MaxHole 决定"块"的合并力度。举例：你用到 D100 和 D125 两个标签，中间 24 个字没人用。'
               'WordMaxHole 默认 10，驱动会发两帧；把它改到 25 以上，就能用一帧把 100 到 125 一次'
               '读回来，代价是多读了 24 个字。标签分散、扫描周期又要求很短时，调大 MaxHole 通常比'
               '调小 RefreshTime 更有效。'))
    S.append(P('MaxBlockSize 不要随手往大改。PLC 对单帧长度有上限，超过会直接回错误码，表现为标签'
               '报 ioPLCError 或 ioIllegalValue；默认的 1920 位 / 120 字是按报文长度和安全余量取的。'))

    # ============================================================ 16.5
    S.append(P('16.5　内存寻址', st_sec))
    S.append(P('一个信捷地址由软元件（M、X、Y、D 等）和编号两部分组成，映射到标签属性上就是'
               '一个代码加一个数字：MemReadFunction 与 MemWriteFunction 填软元件代码，MemAddress '
               '填编号。读写共用同一张表，所以两个功能码填一样的值。'))
    bits = [
        ['代码', '软元件', '数据码', '说明'],
        ['1', 'M', '0x03', '内部继电器（辅助继电器）'],
        ['2', 'X', '0x01', '输入，编号按八进制（见 16.6）'],
        ['3', 'Y', '0x02', '输出，编号按八进制（见 16.6）'],
        ['4', 'S', '0x04', '状态（步进）继电器'],
        ['5', 'SM', '0x0D', '特殊继电器'],
        ['6', 'T', '0x05', '定时器线圈/触点'],
        ['7', 'C', '0x06', '计数器线圈/触点'],
        ['8', 'ET', '0x07', '扩展定时器'],
        ['9', 'HM', '0x08', '高速区继电器 HM'],
        ['10', 'HS', '0x09', '高速区继电器 HS'],
        ['11', 'HT', '0x0A', '高速区继电器 HT'],
        ['12', 'HC', '0x0B', '高速区继电器 HC'],
        ['13', 'HSC', '0x0C', '高速计数器'],
    ]
    S += TBL(bits, [48, 58, 62, 289], '表 16-3　位元件（标签类型只能用布尔）')
    words = [
        ['代码', '软元件', '数据码', '说明'],
        ['17', 'D', '0x80', '数据寄存器'],
        ['18', 'SD', '0x83', '特殊寄存器'],
        ['19', 'TD', '0x81', '定时器当前值'],
        ['20', 'CD', '0x82', '计数器当前值'],
        ['21', 'HD', '0x88', '高速区寄存器 HD'],
        ['22', 'FD', '0x8D', 'FlashROM 寄存器'],
        ['23', 'ID', '0x86', '扩展寄存器 ID'],
        ['24', 'QD', '0x87', '扩展寄存器 QD'],
        ['25', 'ETD', '0x85', '扩展定时器当前值'],
        ['26', 'HSD', '0x8C', '高速区寄存器 HSD'],
        ['27', 'HTD', '0x89', '高速区寄存器 HTD'],
        ['28', 'HCD', '0x8A', '高速区寄存器 HCD'],
        ['29', 'HSCD', '0x8B', '高速计数器当前值'],
        ['30', 'SFD', '0x8E', '系统寄存器 SFD'],
    ]
    S += TBL(words, [48, 58, 62, 289], '表 16-4　字元件（整数、浮点、字符串都挂在字元件上）')
    S.append(P('两个代码之间留了空档（14 到 16），是为了让位元件和字元件各占一段、日后加软元件'
               '不会串号；填表时不用担心，照上表填就行。'))
    S.append(P('定时器和计数器有两个地址：T0、C0 是线圈（位），TD0、CD0 是当前值（字）。要判断'
               '"时间到了没有"用 T/C，要读"现在计到多少"用 TD/CD。这一点与三菱的 TN/CN 相同。'))
    S.append(P('表中"数据码"是报文里跟在命令字后面的那个字节，只在抓包核对时有用，平时不用管；'
               '软元件名称沿用 XDPPro 的助记符，具体地址范围（例如你这台 PLC 的 M 到多少点）'
               '以机型手册为准。'))
    S += NOTE('MemAddress 只填数字。填 "D100" 或 "M0" 会被解析成非法地址，标签不会进入扫描——'
              '这一点与 Modbus 驱动需要填 "4x" 前缀地址的习惯不同。')

    # ============================================================ 16.6
    S.append(P('16.6　X、Y 的八进制编号', st_sec))
    S.append(P('X 和 Y 在信捷 PLC 里按八进制编号：梯形图上写 X0 到 X7、X10 到 X17，其中 X10 其实'
               '是第 8 个输入点。为了让配置和梯形图对得上，驱动默认把 MemAddress 的数字按八进制'
               '解释——IOAddressFormat 为 xiofOctal 时，填 10 表示第 8 点，填 17 表示第 15 点。'))
    S += TBL([
        ['MemAddress', 'xiofOctal（默认）到达的点', 'xiofDecimal 到达的点'],
        ['10', '8', '10'],
        ['17', '15', '17'],
        ['20', '16', '20'],
        ['7', '7', '7'],
    ], [110, 190, 157], '表 16-5　同一个数字在两种格式下指向的物理点')
    S.append(P('如果你习惯按"第几个点"填数，把 IOAddressFormat 改成 xiofDecimal 即可。驱动只在 '
               'X、Y 上做这个转换，M、D、S 等本来就是十进制，不受影响。'))
    S += CODE('''Xinje.IOAddressFormat := xiofDecimal;   // X10 = point #10 now''')
    S += NOTE('这个转换发生在标签登记的时候：格式改完，已经挂在驱动上扫描的标签仍按旧格式访问。'
              '要么在放端口、连标签之前就把格式定好，要么改完把标签重新挂一次'
              '（先把 ProtocolDriver 置 nil，再赋回原驱动），让它们重新登记。')

    # ============================================================ 16.7
    S.append(P('16.7　数据类型与字节序', st_sec))
    S.append(P('字软元件一次读写 16 位（2 字节，高字节在前）。标签的 TagType 只影响它占几个字、'
               '怎么解释这些位，驱动不会因此改变报文长度。'))
    S += TBL([
        ['TagType', '占用', '说明'],
        ['pttByte、pttShortInt', '1 个字', '8 位，只用低字节；读到高字节非 0 说明数据错位'],
        ['pttWord、pttSmallInt', '1 个字', '16 位，无符号 / 有符号'],
        ['pttDWord、pttLongInt', '2 个字', '32 位整数，先读低字再读高字'],
        ['pttFloat', '2 个字', '单精度浮点'],
        ['pttInt64、pttQWord', '4 个字', '64 位整数'],
        ['pttDouble', '4 个字', '双精度浮点'],
        ['pttDefault', '1 个元素', '不指定，由软元件类型决定（位元件 1 位，字元件 1 字）'],
    ], [140, 66, 251], '表 16-6　TagType 与实际占用的字数')
    S.append(P('占两个字的类型（32 位整数、单精度）在 PLC 里是低字在前还是高字在前，取决于 PLC 侧'
               '的指令和你的写入方式。读到明显不对的数值（例如该是 12.5 却读成极小的数），'
               '先把标签的 SwapWords 打开试一次：换过来就对了，说明 PLC 那边是高字在前。'))
    S.append(P('位元件上的标签不要设 32 位或浮点类型——报文里它只占 1 位，多出来的位没有来源，'
               '读到的永远是 0。'))

    # ============================================================ 16.8
    S.append(P('16.8　块、结构体与字符串', st_sec))
    S.append(P('一片连续的软元件用 TPLCBlock 读最划算：一个块一次请求，块内元素由驱动按偏移量分配'
               '给各个 TPLCBlockElement。Size 对位块是位数，对字块是字数。'))
    S.append(P('超过单帧上限的块不用手工拆：驱动会按 WordMaxBlockSize、BitMaxBlockSize 自动切成'
               '多帧；遇到软元件的地址分段点（例如 D 的 20480、S 的 8000、HD 的 6144）也会自动'
               '拆开——这是 PLC 固件对扩展区的限制，一帧跨过分段点会读到错位的数据。'))
    S.append(P('结构体（TPLCStruct）适合映射一台设备的参数区：把 D100 起的 10 个字按 TPLCStructItem '
               '拆成"设定值、上限、下限、实际值"等成员，读一次块就全部刷新，比放十个 TPLCTagNumber '
               '省下九成的报文。'))
    S.append(P('字符串用 TPLCString 挂在字软元件上，一个寄存器装两个字符。StringEncoding 默认按 '
               'UTF-8 与 PLC 的代码页互转，接老设备时如果中文变乱码，改成对应的代码页（如 CP936）'
               '即可。写入时长度不足会补 0，超过 Size 的部分被截断。'))

    # ============================================================ 16.9
    S.append(P('16.9　分步示例', st_sec))
    S.append(P('下面做一个最小可用工程：一个输入点、一个内部继电器、两个数据寄存器（其中一个当'
               '浮点用）。PLC 的 IP 假定为 192.168.6.6，站号 1。'))
    S.append(P('<b>步骤 1：放通信端口。</b>在窗体上放一个 TTCP_UDPPort，Name 改成 TCPPort；Host 填 '
               '192.168.6.6，Port 改成 502，ExclusiveDevice 设 True。'))
    S.append(P('<b>步骤 2：放驱动。</b>再放一个 TXinJETCPDriver，Name 改成 Xinje，把 '
               'CommunicationPort 指向 TCPPort。IOAddressFormat 保持默认的八进制。'))
    S.append(P('<b>步骤 3：建标签。</b>四个标签都设 ProtocolDriver = Xinje，其余按下表填。'))
    S += TBL([
        ['Name', '关键属性', '访问的对象'],
        ['Xinje_D100', 'MemReadFunction 17；MemAddress 100；TagType pttSmallInt；RefreshTime 200',
         'D100，有符号 16 位'],
        ['Xinje_M0', 'MemReadFunction 1；MemAddress 0；TagType pttDefault',
         'M0，位'],
        ['Xinje_X10', 'MemReadFunction 2；MemAddress 10（八进制，即第 8 点）',
         'X10，位'],
        ['Xinje_D200_F', 'MemReadFunction 17；MemAddress 200；TagType pttFloat',
         'D200、D201，浮点'],
    ], [86, 245, 126], '表 16-7　示例工程的四个标签')
    S.append(P('<b>步骤 4：启动。</b>把 TCPPort.Active 设成 True（或运行时点"启动"按钮）。标签开始'
               '按 RefreshTime 刷新，Object Inspector 里能看到 Value 跟着 PLC 变。'))
    S.append(P('<b>步骤 5：验证。</b>在 PLC 里写一个自锁电路让 M0 每 500 ms 翻转一次，画面上放一个 '
               'THMILed 绑到 Xinje_M0，灯闪就说明整条链路通了。'))
    S.append(P('同样的对象写成代码是这样：'))
    S += CODE('''var
  TCPPort: TTCP_UDPPort;
  Xinje: TXinJETCPDriver;
  tag: TPLCTagNumber;
begin
  TCPPort := TTCP_UDPPort.Create(Self);
  TCPPort.Host := '192.168.6.6';
  TCPPort.Port := 502;
  TCPPort.PortType := ptTCP;
  TCPPort.ExclusiveDevice := True;

  Xinje := TXinJETCPDriver.Create(Self);
  Xinje.CommunicationPort := TCPPort;

  tag := TPLCTagNumber.Create(Self);
  tag.Name := 'Xinje_D100';
  tag.PLCStation := 1;
  tag.MemReadFunction := XINJE_FUNC_D;     // 17
  tag.MemWriteFunction := XINJE_FUNC_D;    // 17
  tag.MemAddress := 100;
  tag.TagType := pttSmallInt;
  tag.RefreshTime := 200;
  tag.ProtocolDriver := Xinje;

  TCPPort.Active := True;
end;''')
    S.append(P('XINJE_FUNC_D、XINJE_FUNC_M 这些常量定义在 XinJEDriver 单元里，比直接写 17、1 好读；'
               '表 16-3、表 16-4 的"代码"列与它们一一对应。'))

    # ============================================================ 16.10
    S.append(P('16.10　常见问题', st_sec))
    S.append(P('下面这些现象在实际调试中占九成以上，先按表查一遍再怀疑驱动本身。'))
    S += TBL([
        ['现象', '原因', '处理'],
        ['所有标签都是 ioTimeOut', 'IP 或端口不对；网线不通；PLC 的连接数被 XDPPro 或触摸屏占满',
         '先用 telnet 试 502；断开 XDPPro；ExclusiveDevice 设 True'],
        ['一启动就大面积 ioCommError', '单帧长度超过 PLC 允许值；中间有串口服务器在截断长帧',
         '把 WordMaxBlockSize 降到 120 以内、BitMaxBlockSize 降到 1920 以内再试'],
        ['个别标签 ioPLCError 或 ioIllegalRegAddress', '软元件编号超出机型范围，或该软元件在这台 PLC 上不存在',
         '用 XDPPro 打开软元件表核对编号上限'],
        ['X、Y 读到的点对不上', '八进制与十进制搞混', '梯形图写的 X10 就保持默认八进制；按点数填数就改成 xiofDecimal'],
        ['浮点读成乱码级的小数', '高低字顺序相反', '打开该标签的 SwapWords'],
        ['位写入无效', '位标签建成了 16 位类型；PLC 处于禁止写入状态', '位元件用布尔类型；解除 PLC 保护'],
        ['画面反应慢、报文很多', '标签分散被拆成多帧；RefreshTime 太小', '调大 WordMaxHole、BitMaxHole 合并块，或把同区标签改成 TPLCBlock'],
        ['写入返回错误码 03', '数量或数值超出软元件范围（例如一次写了 200 个字）', '减小块的长度，或按 120 字一帧拆开'],
    ], [116, 176, 165])
    S.append(Spacer(1, 2))

    # ============================================================ 16.11
    S.append(P('16.11　协议帧参考', st_sec))
    S.append(P('抓包核对或者自己写测试程序时，按下面的结构逐字节对。请求和应答都用 Modbus TCP '
               '的 6 字节头，长度域是从站号开始算到报文末尾的字节数。'))
    S += TBL([
        ['字段', '字节', '说明'],
        ['事务号 idH idL', '2', '驱动每帧加 1，应答原样带回'],
        ['协议号 00 00', '2', '固定 0'],
        ['长度 lenH lenL', '2', '站号到报文末尾的字节数'],
        ['站号', '1', 'PLCStation'],
        ['命令字', '1', '1E 读位、1F 写位、20 读字、21 写字'],
        ['数据码', '1', '软元件代码，见表 16-3、表 16-4'],
        ['地址 a2 a1 a0', '3', '24 位大端'],
        ['数量 nH nL', '2', '位或字的个数'],
        ['数据', '0 或 n', '只有写请求才有，位按低位在前打包'],
    ], [110, 52, 295], '表 16-8　请求帧结构')
    S.append(P('应答把"数据码 + 地址 + 数量"这一段换成"字节数 + 数据"：读请求回数据，写请求只回'
               '状态；PLC 拒绝请求时把命令字的最高位置 1（20 变成 A0），并在第一个数据字节给出'
               '错误码，驱动按下面的对应关系转成标签的 IOResult。'))
    S += TBL([
        ['错误码', '驱动返回', '含义'],
        ['01', 'ioIllegalFunction', '命令字不支持'],
        ['02', 'ioIllegalRegAddress', '地址越界或软元件不存在'],
        ['03', 'ioIllegalValue', '数量或数值非法'],
        ['04', 'ioPLCError', 'PLC 内部错误（含写保护）'],
        ['05 / 06 / 07', 'ioAcknowledge / ioBusy / ioNACK', 'PLC 忙或拒绝'],
        ['08', 'ioMemoryParityError', '存储器校验错'],
    ], [60, 176, 221], '表 16-9　错误码与 TProtocolIOResult 的对应')
    S.append(P('几个真实的帧（站号 1）。读 D100 起 10 个字的请求：'))
    S += CODE('''00 00 00 00 00 08 01 20 80 00 00 64 00 0A''')
    S.append(P('写 D100 = 1234（0x04D2）的请求：'))
    S += CODE('''00 00 00 00 00 0B 01 21 80 00 00 64 00 01 02 04 D2''')
    S.append(P('写 M0 到 M3 = 1、0、1、1 的请求（位按低位在前打包成一个字节 0x0D）：'))
    S += CODE('''00 00 00 00 00 0A 01 1F 03 00 00 00 00 04 01 0D''')
    S.append(P('读 D100 起 10 字的应答（设 D100 = 4、D101 = 5，数据共 20 字节）：'))
    S += CODE('''00 00 00 00 00 17 01 20 14 00 04 00 05 ...''')

    # ============================================================ 16.12
    S.append(P('16.12　相关示例', st_sec))
    S.append(P('仓库里暂时没有专门的信捷示例工程，搭法可以照第 5、7 章的示例改：'
               'examples/laz_modbus_tcp_example 演示了"端口 + 驱动 + 标签 + HMI 控件"的最小组合；'
               'examples/laz_isotcp_demonstration 演示了块、结构体、字符串和位标签混在同一个'
               '工程里的写法。'))
    S.append(P('驱动随 pascalscada.lpk 一起编译，单元为 XinJEDriver（软元件表、地址翻译、块管理、'
               '扫描）和 XinJETCP（报文编解码）。自己写协议测试程序时，把两个单元加进 uses，再用'
               '一个假的 TCommPortDriver 回放字节，就能不开 PLC 验证帧格式和取值。'))
    S.append(P('本章的软元件表与驱动里的表一一对应。日后驱动新增软元件，只需在 XinJEDriver 的'
               'XINJE_DEV_FUNC、XINJE_DEV_NAME、XINJE_DEV_DATACODE 等并行数组里加一项，本章的'
               '表 16-3、表 16-4 也相应补一行即可。'))

    doc.build(S)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'xinje_chapter.pdf'
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 86
    build(out, start)
    print('written', out)
