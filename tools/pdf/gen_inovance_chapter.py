# -*- coding: utf-8 -*-
"""
生成《PascalSCADA 中文使用手册》新增章节: 第 19 章 汇川 PLC（Modbus TCP）

页面规格与原手册一致:
  A4 595.32 x 841.92, 版心左 68.1 / 右 525.4, 正文 10.6pt 宋体, 章标题 16pt,
  节标题 13.6pt 黑体, 页脚居中页码 9pt。

用法: python gen_inovance_chapter.py <输出 pdf 路径> [起始页码]
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
    def __init__(self, filename, first_page_no=109):
        BaseDocTemplate.__init__(self, filename, pagesize=A4,
                                 leftMargin=LEFT, rightMargin=RIGHT,
                                 topMargin=PAGE_H - TOP, bottomMargin=BOTTOM,
                                 title='PascalSCADA 中文使用手册',
                                 author='PascalSCADA 中文手册',
                                 subject='第 19 章 汇川 PLC（Modbus TCP）')
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


def build(path, first_page_no=109):
    doc = ManualDoc(path, first_page_no)
    S = []

    # ============================================================ 章标题
    S.append(P('第 19 章　汇川 PLC（Modbus TCP）', st_chap))
    S.append(P('19.1　简介', st_sec))
    S.append(P('TInovanceTCPDriver 是汇川（Inovance）PLC 的以太网驱动，走标准 Modbus TCP，'
               'TCP 端口 502。适用于三类机型：H5U/Easy 系列（本体带网口）、H3U/XP 系列'
               '（加以太网板），以及 AM400/AM600/AM800、AC800 等中型控制器。'
               '这些机型的以太网口都开放 Modbus TCP 从站服务，驱动直接与之通信，'
               '不依赖汇川的任何 DLL。'))
    S.append(P('和第 18 章的台达驱动一样，报文就是普通 Modbus TCP，驱动的价值在于<b>地址映射</b>：'
               '标签里直接填 M100、D200，由驱动按汇川的映射表换算。但汇川有三个系列，'
               '三个系列的软元件范围和映射表都不一样，所以驱动用 Series 属性切换：'
               'ivsH5U、ivsH3U、ivsAM，出厂默认 ivsH5U。'))
    S.append(P('汇川驱动还有一个特殊设计：AM 系列里 Q（输出）和 M（中间继电器）两个软元件'
               '共享同一段线圈区，光看应答报文分不清读的是哪一个。驱动给每一帧请求记下'
               '"事务号 → 软元件"的对应关系，应答带回了事务号，按事务号找回软元件——'
               '所以即使两个软元件地址完全重叠，各自的标签也能正确刷新。'))
    S += NOTE('本章与第 16～18 章同为后补章节。Modbus 的通用概念（线圈、保持寄存器、功能码）'
              '见第 11 章；台达驱动的用法结构与之非常相似，可以对照第 18 章看。')

    # ============================================================ 19.2
    S.append(P('19.2　所需组件', st_sec))
    S += TBL([
        ['对象', '属性', '填什么'],
        ['通信端口\nTTCP_UDPPort', 'Host', 'PLC 的 IP，例如 192.168.1.30'],
        ['', 'Port', '502（Modbus TCP 标准端口，也是该组件的默认值）'],
        ['', 'PortType', 'ptTCP'],
        ['协议驱动\nTInovanceTCPDriver', 'CommunicationPort', '指向上面那个 TTCP_UDPPort'],
        ['', 'Series', 'ivsH5U / ivsH3U / ivsAM，见 19.3'],
        ['', 'ReadOnly', '默认 False；只监视不控制时置 True'],
        ['标签\n（TPLCTagNumber 等）', 'PLCStation', 'Modbus 站号（unit id），汇川默认 1'],
        ['', 'MemReadFunction / MemWriteFunction', '软元件编号，见表 19-2，读写必须填同一个'],
        ['', 'MemAddress', '软元件内的地址，见表 19-3 的写法'],
        ['', 'RefreshTime', '刷新周期，毫秒。默认 1000，调试时可设 200'],
    ], [140, 138, 179], '表 19-1　一个最小可用的对象组合')
    S.append(P('在代码里创建这些对象需要引用下面的单元：'))
    S += CODE('''uses
  tcp_udpport, InovanceTCP, PLCTagNumber, ProtocolTypes;''')
    S.append(P('驱动单元 InovanceTCP（及其基类单元 InovanceDriver）编译在 pascalscada.lpk 里，'
               '控件显示在组件面板的 Protocols 页，名字是 TInovanceTCPDriver。'))
    S += NOTE('Series 必须在把标签挂上驱动<b>之前</b>设置好：地址换算发生在标签登记的那一刻，'
              '先挂标签后换系列，已登记的地址还是按旧系列换算的，要重新挂一次才生效。'
              '这一点与台达驱动相同。')

    # ============================================================ 19.3
    S.append(P('19.3　准备 PLC 与选择系列', st_sec))
    S.append(NUM(1, '<b>确认网口可用。</b>H5U/Easy 本体自带一个网口；H3U 要加 H3U-ETH 以太网板；'
                   'AM400/600/800、AC800 本体带网口。用 AutoShop（H5U/AM 用 AutoShop，'
                   'H3U 用 AutoShop for XP）把 IP 设好，上位机网卡设到同一网段。'))
    S.append(NUM(2, '<b>打开 Modbus TCP 从站。</b>H5U 的 Modbus TCP 服务默认开启；'
                   'AM 系列在 AutoShop 的控制器属性里确认以太网口协议配置；'
                   'H3U 以太网板用配套工具配置。'))
    S.append(NUM(3, '<b>确定站号。</b>默认 1。标签的 PLCStation 填这个值。'))
    S.append(NUM(4, '<b>选对系列。</b>Series 按机型选：H5U/Easy 选 ivsH5U，H3U/XP 选 ivsH3U，'
                   'AM400/600/800、AC800 选 ivsAM。选错的典型症状是"能通信但地址对不上"'
                   '或者报非法地址（02）。'))
    S.append(NUM(5, '<b>先验端口。</b>命令行执行 telnet 192.168.1.30 502。窗口清空并出现光标'
                   '说明端口通；提示失败就先查 IP、网线和防火墙，不要怀疑驱动。'))
    S += NOTE('H5U 的 Modbus TCP 连接数很少（约 4～8 个），AM 系列多几个。调试时若遇到'
              '"能连上、偶尔掉线"，先确认没有其它上位机、组态软件同时占着连接。')

    # ============================================================ 19.4
    S.append(P('19.4　驱动属性', st_sec))
    S += TBL([
        ['属性', '默认值', '说明'],
        ['Series', 'ivsH5U', '地址映射所用的系列：ivsH5U、ivsH3U 或 ivsAM。'
                            '必须在挂标签之前设好'],
        ['IOAddressFormat', 'ivoOctal', 'H3U/H5U 的 X、Y 编号方式：ivoOctal 把地址数字按八进制读'
                                       '（X17 → 第 15 点）；ivoDecimal 按十进制读。AM 系列忽略此项'],
        ['ReadOnly', 'False', '置 True 后不再发送任何写请求，只监视'],
        ['ReadSomethingAlways', 'True', '每个扫描周期至少读一个块，保持链路活跃'],
        ['BitMaxHole', '50', '一个块内允许多少个位没被任何标签声明仍算连续'],
        ['WordMaxHole', '10', '同上，对字软元件'],
        ['BitMaxBlockSize', '1920', '一帧最多读多少个位（Modbus 上限 2000，留了余量）'],
        ['WordMaxBlockSize', '120', '一帧最多读多少个字（Modbus 上限 125，留了余量）'],
    ], [110, 78, 269], '表 19-2　TInovanceTCPDriver 的属性')

    # ============================================================ 19.5
    S.append(P('19.5　地址映射', st_sec))
    S.append(P('三个系列的软元件和映射汇总如下。编号列是 MemReadFunction/MemWriteFunction '
               '要填的值；不支持的组合在该系列里不可用（登记标签时会被忽略）。'))
    S += TBL([
        ['软元件', '编号', '类型', 'AM', 'H3U', 'H5U'],
        ['M',  '1',  '位', '原值', '原值', '原值'],
        ['Q',  '2',  '位', '十进制位偏移', '—', '—'],
        ['I',  '3',  '位', '十进制位偏移（只读）', '—', '—'],
        ['X',  '4',  '位', '—', '八进制后 +63488（只读）', '八进制后 +63488（只读）'],
        ['Y',  '5',  '位', '—', '八进制后 +64512', '八进制后 +64512'],
        ['S',  '6',  '位', '—', '+57344', '+57344'],
        ['B',  '7',  '位', '—', '—', '+12288'],
        ['D',  '17', '字', '—', '原值', '原值'],
        ['MW', '18', '字', '原值', '—', '—'],
        ['MD', '19', '字', '地址 ×2，占 2 寄存器', '—', '—'],
        ['R',  '20', '字', '—', '+12288', '+12288'],
        ['SD', '21', '字', '—', '+9216', '—'],
        ['T',  '22', '字', '—', '+61440', '—'],
        ['C',  '23', '字', '—', 'C200 前后映射不同，见正文', '—'],
    ], [46, 40, 34, 110, 135, 92], '表 19-3　软元件编号与地址映射')
    S.append(P('位偏移的写法说明：AM 的 Q、I 在 AutoShop 里按"字节.位"书写（Q10.3 = 第 10 字节'
               '第 3 位），MemAddress 填十进制位偏移：10×8+3 = 83。H3U/H5U 的 X、Y 按八进制'
               '书写（X17 = 第 15 点），MemAddress 直接填 17，驱动按八进制读；带位的形式'
               'X10.3 换算成八进制(10)×8+3 = 67 后填入。M 一律十进制。'))
    S.append(P('H3U 的字计数器 C 要特别注意：C0～C199 是 16 位计数器，各占 1 个寄存器；'
               'C200 起是 32 位计数器，各占 2 个寄存器，映射也跳到了另一段。驱动会在'
               '跨 C200 分界处自动拆帧，但<b>建议把 C0～C199 和 C200 以上分成两个标签</b>，'
               '不要用一个标签横跨分界，否则分界附近的值没有意义。'))
    S += TBL([
        ['梯形图地址', 'MemAddress 填', '换算成 Modbus 地址'],
        ['H5U D100', '100', '100（寄存器）'],
        ['H5U X17', '17', '八进制 17 = 15，+63488 = 63503（离散输入）'],
        ['H5U Y7', '7', '64512 + 7 = 64519（线圈）'],
        ['H5U B100', '100', '12288 + 100 = 12388'],
        ['H3U C50', '50', '62464 + 50 = 62514'],
        ['H3U C250', '250', '(250-200)×2 + 63232 = 63332'],
        ['AM Q10.3', '83', '10×8+3 = 83（线圈）'],
        ['AM MD50', '50', '50×2 = 100 起，占 2 个寄存器'],
    ], [104, 118, 235], '表 19-4　换算举例')
    S += NOTE('I 和 X 是物理输入，两个系列里都只能读。给它们发写请求，编码阶段就会被拒绝，'
              '不会发出任何报文。需要控制时用 Q（AM）或 Y（H3U/H5U）。')

    # ============================================================ 19.6
    S.append(P('19.6　数据宽度与 32 位数据', st_sec))
    S.append(P('位软元件（编号 1～7）一个标签一位，TagType 用 pttByte；字软元件（编号 17～23）'
               '一个标签一个 16 位字。32 位数据（DINT、REAL）占两个连续寄存器，'
               '用 TPLCBlock 或把 Size 设为 2 来读。'))
    S.append(P('字序与台达相同：低 16 位在低地址（CDAB）。用 TPLCBlock 读 32 位数据时，'
               '第 0 个块元素是低字。AM 系列的 MD 本身就是双字软元件，一个 MD 标签占 2 个'
               '寄存器，Size 填 2 即可拿到完整的 32 位值。'))
    S.append(P('浮点数用 pttFloat 读两个连续寄存器。读回来是乱码时，优先怀疑：地址没有对齐、'
               'TagType 选错、或把低字高字读反。'))

    # ============================================================ 19.7
    S.append(P('19.7　分步示例', st_sec))
    S.append(P('下面做一个 H5U 的最小工程：PLC 在 192.168.1.30，站号 1。读一个字（D100）、'
               '一个位（M100），写一个字（D200）。'))
    S.append(P('<b>步骤 1：放端口。</b>窗体上放一个 TTCP_UDPPort，Name 改成 TCPPort；Host 填 '
               '192.168.1.30，Port 保持 502，PortType 保持 ptTCP。'))
    S.append(P('<b>步骤 2：放驱动。</b>再放一个 TInovanceTCPDriver，Name 改成 Inov，'
               'CommunicationPort 指向 TCPPort，Series 保持 ivsH5U，ReadOnly 保持 False。'))
    S.append(P('<b>步骤 3：建标签。</b>按下表填，三个都是 TPLCTagNumber。'))
    S += TBL([
        ['Name', '关键属性', '访问的对象'],
        ['Inov_D100', 'PLCStation 1；MemReadFunction/WriteFunction 17；MemAddress 100；'
                      'TagType pttSmallInt；RefreshTime 200', 'D100 字'],
        ['Inov_M100', 'PLCStation 1；MemReadFunction/WriteFunction 1；MemAddress 100；'
                      'TagType pttByte', 'M100 位'],
        ['Inov_D200', 'PLCStation 1；MemReadFunction/WriteFunction 17；MemAddress 200；'
                      'TagType pttSmallInt', 'D200 字（可写）'],
    ], [96, 268, 93], '表 19-5　示例工程的三个标签')
    S.append(P('<b>步骤 4：启动。</b>把 TCPPort.Active 设成 True。D100、M100 按各自的 RefreshTime '
               '扫描；往 Inov_D200.Value 写一个数，驱动按站号 1、功能码 06 发出写单寄存器请求。'))
    S.append(P('<b>步骤 5：验证。</b>在 AutoShop 里在线监视 D100、M100，与画面上的值比对；'
               '再从画面改 D200，看 AutoShop 里的值是否跟着变。两边一致，链路就算通了。'))
    S.append(P('同样的对象写成代码是这样：'))
    S += CODE('''var
  TCPPort: TTCP_UDPPort;
  Inov: TInovanceTCPDriver;
  tagD100, tagM100, tagD200: TPLCTagNumber;
begin
  TCPPort := TTCP_UDPPort.Create(Self);
  TCPPort.Host := '192.168.1.30';
  TCPPort.Port := 502;
  TCPPort.PortType := ptTCP;

  Inov := TInovanceTCPDriver.Create(Self);
  Inov.Series := ivsH5U;
  Inov.CommunicationPort := TCPPort;

  tagD100 := TPLCTagNumber.Create(Self);
  tagD100.MemReadFunction  := 17;
  tagD100.MemWriteFunction := 17;
  tagD100.MemAddress  := 100;
  tagD100.TagType     := pttSmallInt;

  tagM100 := TPLCTagNumber.Create(Self);
  tagM100.MemReadFunction  := 1;
  tagM100.MemWriteFunction := 1;
  tagM100.MemAddress  := 100;
  tagM100.TagType     := pttByte;

  tagD100.ProtocolDriver := Inov;
  tagM100.ProtocolDriver := Inov;

  TCPPort.Active := True;
end;''')
    S.append(P('H3U 和 AM 系列的用法完全一样，只有两处不同：Inov.Series 改成对应系列；'
               '软元件换成该系列支持的编号（表 19-3）。AM 系列的 Q、I 记得按位偏移换算。'))

    # ============================================================ 19.8
    S.append(P('19.8　常见问题', st_sec))
    S += TBL([
        ['现象', '原因', '处理'],
        ['全部标签 ioTimeOut', 'IP、端口不对；防火墙；连接数被占满',
         'telnet 试 502；断开其它上位机；H5U 连接数只有几个'],
        ['能通信但地址对不上', 'Series 选错系列',
         '按机型改 Series 后重新挂标签'],
        ['全部标签 ioIllegalRegAddress（02）',
         '软元件不在该系列映射里，或地址超范围',
         '对照表 19-3；查该机型的软元件范围表'],
        ['写入 X 或 I 没有反应', '物理输入只能读',
         '改用 Y（H3U/H5U）或 Q（AM）'],
        ['AM 的 Q 和 M 值互相串', '正常现象：两个软元件共享同一段线圈区',
         '驱动按事务号区分，标签各自刷新正确；若怀疑串了先核对 PLC 程序'],
        ['H3U 的 C 值错乱', '一个标签跨了 C200 分界，两段映射不同',
         'C0～C199 和 C200 以上分成两个标签'],
        ['32 位数高低颠倒', 'CDAB 字序，两个字读反了',
         '低字在前：第一个寄存器是低 16 位，见 19.6'],
        ['浮点读成乱码', 'TagType 不对，或地址没有对齐',
         'REAL 用 pttFloat 读两个连续寄存器'],
    ], [138, 190, 129])
    S.append(Spacer(1, 2))

    # ============================================================ 19.9
    S.append(P('19.9　协议参考', st_sec))
    S.append(P('线上的报文就是标准 Modbus TCP，帧结构见第 18 章表 18-6。'
               '功能码：01 读线圈、02 读离散输入（I、X）、03 读保持寄存器、05 写单线圈、'
               '06 写单寄存器、15 写多线圈、16 写多寄存器，与表 18-7 相同；'
               '异常码到 IOResult 的对应关系见表 18-8。'))
    S.append(P('汇川驱动特有的机制是事务号反查：AM 系列里 Q 和 M 共享同一段线圈区'
               '（都从线圈 0 开始映射），仅凭应答报文里的地址无法区分读的是哪个软元件。'
               '驱动在发出每一帧请求时，把"事务号 → 软元件"登记进一张 256 项的环形表；'
               'Modbus TCP 的应答会原样带回事务号，解码时按事务号查表找回软元件，'
               '再把数值写进对应的内存区。该表按事务号取模复用，正常请求-应答节奏下'
               '不会发生覆盖。'))
    S.append(P('表 19-3 与 InovanceDriver 单元里的 INOVANCE_DEV_* 常量、DeviceAddress 函数'
               '一一对应；事务号反查对应 EncodePkg/DecodePkg 里的 PWireDevMap。'
               '驱动扩展软元件时，同步更新表 19-3 即可。'))
    S.append(P('驱动随 pascalscada.lpk 一起编译，单元是 InovanceTCP（Modbus TCP 帧编解码、'
               '事务号反查）和 InovanceDriver（地址映射、内存管理、扫描），纯 Pascal 实现，'
               '不依赖任何 DLL，可以编译到 Win32/Win64/Linux 各个平台。地址映射和帧格式'
               '有 56 项自测（tools/inovancetest.lpr），改动驱动后跑一遍即可回归。'))

    doc.build(S)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'inovance_chapter.pdf'
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 109
    build(out, start)
    print('written', out)
