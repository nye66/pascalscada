# -*- coding: utf-8 -*-
"""
生成《PascalSCADA 中文使用手册》新增章节: 第 18 章 台达 PLC（Modbus TCP）

页面规格与原手册一致:
  A4 595.32 x 841.92, 版心左 68.1 / 右 525.4, 正文 10.6pt 宋体, 章标题 16pt,
  节标题 13.6pt 黑体, 页脚居中页码 9pt。

用法: python gen_delta_chapter.py <输出 pdf 路径> [起始页码]
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
    def __init__(self, filename, first_page_no=102):
        BaseDocTemplate.__init__(self, filename, pagesize=A4,
                                 leftMargin=LEFT, rightMargin=RIGHT,
                                 topMargin=PAGE_H - TOP, bottomMargin=BOTTOM,
                                 title='PascalSCADA 中文使用手册',
                                 author='PascalSCADA 中文手册',
                                 subject='第 18 章 台达 PLC（Modbus TCP）')
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


def build(path, first_page_no=102):
    doc = ManualDoc(path, first_page_no)
    S = []

    # ============================================================ 章标题
    S.append(P('第 18 章　台达 PLC（Modbus TCP）', st_chap))
    S.append(P('18.1　简介', st_sec))
    S.append(P('TDeltaTCPDriver 是台达（Delta）PLC 的以太网驱动，走标准 Modbus TCP，'
               'TCP 端口 502。台达的 DVP 系列（ES2/SE/SX2 等）配上以太网模块或选用带网口的机型、'
               'AS 系列的控制器自带网口，都开放 Modbus TCP 从站服务，本驱动直接与之通信，'
               '不依赖台达的任何 DLL。'))
    S.append(P('台达驱动和第 11 章 Modbus TCP 驱动用的是同一套报文，区别只有一个：<b>地址映射</b>。'
               'Modbus 驱动要求用户自己把 M100 换算成线圈 3072、把 D200 换算成保持寄存器 4296；'
               '台达驱动里直接填 M100、D200，由驱动按台达的映射表换算。两套映射还不一样——'
               'DVP 系列和 AS 系列各有一张表，所以驱动有一个 Series 属性用来切换。'))
    S.append(P('X、Y 这两个输入/输出继电器是物理端子：X 只能读不能写；DVP 系列的 X、Y 按'
               '八进制编号（X17 是第 15 个点），驱动的 IOAddressFormat 默认按八进制读地址，'
               '和梯形图上的写法一致。AS 系列的 X、Y 按十进制位偏移填。'))
    S += NOTE('本章与第 16、17 章同为后补章节，排在手册末尾。Modbus 的通用概念（线圈、保持寄存器、'
              '功能码）见第 11 章，本章不再重复；标签、扫描、块这些基础概念见第 4 章。')

    # ============================================================ 18.2
    S.append(P('18.2　所需组件', st_sec))
    S.append(P('和信捷、三菱驱动一样，三个对象就够：端口、驱动、标签。'))
    S += TBL([
        ['对象', '属性', '填什么'],
        ['通信端口\nTTCP_UDPPort', 'Host', 'PLC 的 IP，例如 192.168.1.5'],
        ['', 'Port', '502（Modbus TCP 标准端口，也是该组件的默认值）'],
        ['', 'PortType', 'ptTCP'],
        ['协议驱动\nTDeltaTCPDriver', 'CommunicationPort', '指向上面那个 TTCP_UDPPort'],
        ['', 'Series', 'dvsDvp 或 dvsAS，见 18.3'],
        ['', 'ReadOnly', '默认 False；只监视不控制时置 True'],
        ['标签\n（TPLCTagNumber 等）', 'PLCStation', 'Modbus 站号（unit id），台达出厂默认 1'],
        ['', 'MemReadFunction / MemWriteFunction', '软元件编号，见表 18-2，读写必须填同一个'],
        ['', 'MemAddress', '软元件内的地址，例如 100 代表 D100、M100'],
        ['', 'RefreshTime', '刷新周期，毫秒。默认 1000，调试时可设 200'],
    ], [130, 138, 189], '表 18-1　一个最小可用的对象组合')
    S.append(P('在代码里创建这些对象需要引用下面的单元：'))
    S += CODE('''uses
  tcp_udpport, DeltaTCP, PLCTagNumber, ProtocolTypes;''')
    S.append(P('驱动单元 DeltaTCP（及其基类单元 DeltaDriver）编译在 pascalscada.lpk 里，'
               '控件显示在组件面板的 Protocols 页，名字是 TDeltaTCPDriver。'))
    S += NOTE('Series 必须在把标签挂上驱动<b>之前</b>设置好：地址换算发生在标签登记的那一刻，'
              '先挂标签后换系列，已登记的地址还是按旧系列换算的，要重新挂一次才生效。')

    # ============================================================ 18.3
    S.append(P('18.3　准备 PLC 与选择系列', st_sec))
    S.append(P('上电前按下面几条检查，能省掉大部分"连不上"。'))
    S.append(NUM(1, '<b>确认网口可用。</b>DVP-ES2/SS2 本体没有网口，要配 DVPEN01-SL 或 IFD9506 这类'
                   '以太网模块；DVP-SE/SX2/WAC 带网口；AS 系列本体自带。模块型机器要先用'
                   'DCISoft 或模块配置工具把 IP 设好，再把上位机网卡设到同一网段。'))
    S.append(NUM(2, '<b>打开 Modbus TCP 从站。</b>DVP 系列 PLC 默认就开 502 端口的 Modbus 服务，'
                   '个别机型要在 WPLSoft 的"周边设置－通信设置"里确认；AS 系列用 ISPSoft 的'
                   'HWCONFIG 检查网口配置。'))
    S.append(NUM(3, '<b>确定站号。</b>台达默认站号是 1。标签的 PLCStation 填这个值；'
                   '多台 PLC 串在一条 Modbus TCP 网关后面时才需要区分站号。'))
    S.append(NUM(4, '<b>选对系列。</b>Series = dvsDvp 适用于 DVP 全系（含通过网关透传的场合）；'
                   'Series = dvsAS 适用于 AS200/300/400 系列控制器。两系列的软元件范围和地址映射'
                   '都不同，选错了轻则读回乱数据，重则报非法地址。'))
    S.append(NUM(5, '<b>先验端口。</b>命令行执行 telnet 192.168.1.5 502。窗口清空并出现光标'
                   '说明端口通；提示失败就先查 IP、网线和防火墙，不要怀疑驱动。'))
    S += NOTE('一个 502 端口通常只接受有限个 TCP 连接（DVP 以太网模块一般 8 到 16 个）。'
              '调试时若遇到"能连上、偶尔掉线"，先确认没有别上位机、组态软件同时占着连接。')

    # ============================================================ 18.4
    S.append(P('18.4　驱动属性', st_sec))
    S += TBL([
        ['属性', '默认值', '说明'],
        ['Series', 'dvsDvp', '地址映射所用的系列：dvsDvp（DVP 全系）或 dvsAS（AS 系列）。'
                            '必须在挂标签之前设好'],
        ['IOAddressFormat', 'dvfOctal', 'DVP 系列 X、Y 的编号方式：dvfOctal 把地址数字按八进制读'
                                       '（X17 → 第 15 点）；dvfDecimal 按十进制读。AS 系列忽略此项'],
        ['ReadOnly', 'False', '置 True 后不再发送任何写请求，只监视'],
        ['ReadSomethingAlways', 'True', '每个扫描周期至少读一个块，保持链路活跃'],
        ['BitMaxHole', '50', '一个块内允许多少个位没被任何标签声明仍算连续'],
        ['WordMaxHole', '10', '同上，对字软元件'],
        ['BitMaxBlockSize', '1920', '一帧最多读多少个位（Modbus 上限 2000，留了余量）'],
        ['WordMaxBlockSize', '120', '一帧最多读多少个字（Modbus 上限 125，留了余量）'],
    ], [110, 78, 269], '表 18-2　TDeltaTCPDriver 的属性')
    S.append(P('BitMaxBlockSize 和 WordMaxBlockSize 一般不用动。调大能减少帧数，但超过 Modbus '
               '协议上限（2000 位 / 125 字）PLC 会直接回异常；调小则帧数变多、扫描变慢。'))

    # ============================================================ 18.5
    S.append(P('18.5　地址映射', st_sec))
    S.append(P('标签的 MemReadFunction/MemWriteFunction 填软元件编号，MemAddress 填编号内的地址'
               '（十进制数字）。驱动按下表把"软元件 + 地址"换算成 Modbus 地址再发帧，'
               '所以 MemAddress 填的就是梯形图里写的那个数字。'))
    S += TBL([
        ['软元件', '编号', '类型', 'DVP 映射', 'AS 映射'],
        ['M', '1', '位', '+2048；M1536 及以上另起一段', '原值'],
        ['X', '2', '位', '八进制后 +1024（只读，02 功能码）', '十进制位偏移 +24576（只读）'],
        ['Y', '3', '位', '八进制后 +1280', '十进制位偏移 +40960'],
        ['S', '4', '位', '原值', '+20480'],
        ['T', '5', '位', '+1536', '+57344'],
        ['C', '6', '位', '+3584', '+61440'],
        ['SM', '7', '位', '—（DVP 无此软元件）', '+16384'],
        ['HC', '8', '位', '—（DVP 无此软元件）', '+64512'],
        ['D', '17', '字', '+4096；D4096 及以上另起一段', '原值'],
        ['TD', '18', '字', '+1536', '+57344'],
        ['CD', '19', '字', '+3584', '+61440'],
        ['SR', '20', '字', '—（DVP 无此软元件）', '+49152'],
        ['HCD', '21', '字', '—（DVP 无此软元件）', '+64512'],
        ['E', '22', '字', '—（DVP 无此软元件）', '+65024'],
    ], [46, 40, 36, 200, 135], '表 18-3　软元件编号与地址映射')
    S.append(P('几个换算例子（DVP 系列）：'))
    S += TBL([
        ['梯形图地址', 'MemAddress 填', '换算成 Modbus 地址'],
        ['D100', '100', '4096 + 100 = 4196（寄存器）'],
        ['D5000', '5000', '5000 - 4096 + 36864 = 37768（扩展区寄存器）'],
        ['M100', '100', '2048 + 100 = 2148（线圈）'],
        ['M1600', '1600', '1600 - 1536 + 45056 = 45120（扩展区线圈）'],
        ['X17', '17', '八进制 17 = 十进制 15，+1024 = 1039（离散输入）'],
        ['Y7', '7', '1280 + 7 = 1287（线圈）'],
        ['C50（位）', '50', '3584 + 50 = 3634'],
        ['CD250（字）', '250', '3584 + 250 = 3834'],
    ], [104, 118, 235], '表 18-4　DVP 系列换算举例')
    S.append(P('M 的 1536 分界和 D 的 4096 分界是台达自己的地址断层：M0～M1535 映射到线圈区，'
               'M1536 起映射到另一段；D0～D4095 和 D4096 起同理。一个读请求不能跨过断层，'
               '驱动检测到跨断层时会自动拆成两帧，标签侧没有任何感觉，不用手工处理。'))
    S += NOTE('X 在两个系列里都只能读。给 X 的标签发写请求，编码阶段就会被拒绝（返回非法功能），'
              '不会发出任何报文。需要控制时用 Y。')

    # ============================================================ 18.6
    S.append(P('18.6　数据宽度与 32 位数据', st_sec))
    S.append(P('位软元件（编号 1～8）的一个标签就是一位，TagType 用 pttByte 即可；'
               '字软元件（编号 17～22）的一个标签是一个 16 位字，按 TagType 解释。'
               '32 位数据（DINT、双字计数器、浮点）占两个连续地址，用 TPLCBlock 或'
               '把 TPLCTagNumber 的 Size 设为 2 来读。'))
    S.append(P('要注意字序：台达的 32 位数据是 CDAB 存放——低 16 位在低地址，高 16 位在高地址'
               '（与西门子相反）。用两个 16 位标签自己拼 32 位时，低字是第一个地址；'
               '用 TPLCBlock 整块读时，块元素按地址顺序排列，第 0 个元素就是低字。'
               '发现 32 位值"高低颠倒"时，先核对是不是把两个字读反了。'))
    S.append(P('浮点数用 pttFloat 读两个连续的 D 寄存器（DVP 的 REAL 就是这样存放的）。'
               '读回来是乱码时，优先怀疑：地址不是偶数对齐、TagType 选错、或把 CDAB 的两个字读反。'))

    # ============================================================ 18.7
    S.append(P('18.7　分步示例', st_sec))
    S.append(P('下面做一个 DVP-ES2 加以太网模块的最小工程：PLC 在 192.168.1.5，站号 1。'
               '读一个字（D100）、一个位（M100），写一个字（D200）。'))
    S.append(P('<b>步骤 1：放端口。</b>窗体上放一个 TTCP_UDPPort，Name 改成 TCPPort；Host 填 '
               '192.168.1.5，Port 保持 502，PortType 保持 ptTCP。'))
    S.append(P('<b>步骤 2：放驱动。</b>再放一个 TDeltaTCPDriver，Name 改成 Delta，'
               'CommunicationPort 指向 TCPPort，Series 保持 dvsDvp，ReadOnly 保持 False。'))
    S.append(P('<b>步骤 3：建标签。</b>按下表填，三个都是 TPLCTagNumber。'))
    S += TBL([
        ['Name', '关键属性', '访问的对象'],
        ['Delta_D100', 'PLCStation 1；MemReadFunction/WriteFunction 17；MemAddress 100；'
                       'TagType pttSmallInt；RefreshTime 200', 'D100 字'],
        ['Delta_M100', 'PLCStation 1；MemReadFunction/WriteFunction 1；MemAddress 100；'
                       'TagType pttByte', 'M100 位'],
        ['Delta_D200', 'PLCStation 1；MemReadFunction/WriteFunction 17；MemAddress 200；'
                       'TagType pttSmallInt', 'D200 字（可写）'],
    ], [96, 268, 93], '表 18-5　示例工程的三个标签')
    S.append(P('<b>步骤 4：启动。</b>把 TCPPort.Active 设成 True。D100、M100 按各自的 RefreshTime '
               '扫描；往 Delta_D200.Value 写一个数，驱动按站号 1、功能码 06 发出写单寄存器请求。'))
    S.append(P('<b>步骤 5：验证。</b>在 WPLSoft 里在线监视 D100、M100，与画面上的值比对；'
               '再从画面改 D200，看 WPLSoft 里的值是否跟着变。两边一致，链路就算通了。'))
    S.append(P('同样的对象写成代码是这样：'))
    S += CODE('''var
  TCPPort: TTCP_UDPPort;
  Delta: TDeltaTCPDriver;
  tagD100, tagM100, tagD200: TPLCTagNumber;
begin
  TCPPort := TTCP_UDPPort.Create(Self);
  TCPPort.Host := '192.168.1.5';
  TCPPort.Port := 502;
  TCPPort.PortType := ptTCP;

  Delta := TDeltaTCPDriver.Create(Self);
  Delta.Series := dvsDvp;
  Delta.CommunicationPort := TCPPort;

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

  tagD100.ProtocolDriver := Delta;
  tagM100.ProtocolDriver := Delta;

  TCPPort.Active := True;
end;''')
    S.append(P('AS 系列的用法完全一样，只有两处不同：Delta.Series 改成 dvsAS；'
               'SM、SR、HC、HCD、E 这些软元件开始可用，编号见表 18-3。'))

    # ============================================================ 18.8
    S.append(P('18.8　常见问题', st_sec))
    S += TBL([
        ['现象', '原因', '处理'],
        ['全部标签 ioTimeOut', 'IP、端口不对；防火墙；连接数被占满',
         'telnet 试 502；断开其它上位机；核对网段'],
        ['全部标签 ioIllegalRegAddress（02）',
         'Series 选错（AS 的映射套在 DVP 上或反之）；地址超出该软元件范围',
         '确认 PLC 系列，改 Series 后重新挂标签'],
        ['个别标签 ioIllegalRegAddress',
         '地址超范围，例如 DVP 的 D 只到 D11999、M 只到 M1535（加扩展后更多）',
         '查该机型的软元件范围表'],
        ['写入 X 没有反应', 'X 是物理输入，只能读',
         '改用对应的 Y 输出点'],
        ['读到的 32 位数高低颠倒', 'CDAB 字序，两个字读反了',
         '低字在前：第一个地址是低 16 位，见 18.6'],
        ['浮点读成乱码', 'TagType 不对，或地址没有对齐到偶数',
         'REAL 用 pttFloat 读两个连续 D；确认 D 地址成对'],
        ['M1500 附近的值错乱',
         '手工用 Modbus 驱动直填 Modbus 地址时跨了 1536 分界',
         '改用本驱动按 M 编号填，分界由驱动自动拆帧处理'],
        ['扫描周期越来越长', '标签太散，块合并不起来',
         '集中地址；放宽 RefreshTime；加大 MaxHole'],
    ], [138, 190, 129])
    S.append(Spacer(1, 2))

    # ============================================================ 18.9
    S.append(P('18.9　协议参考', st_sec))
    S.append(P('线上的报文就是标准 Modbus TCP。抓包核对时按下面的结构看：'))
    S += TBL([
        ['字节', '含义', '说明'],
        ['0～1', '事务标识', '驱动递增分配，应答原样带回'],
        ['2～3', '协议标识', '固定 0000'],
        ['4～5', '长度', '第 6 字节起的字节数'],
        ['6', '单元标识符', '标签的 PLCStation（站号）'],
        ['7', '功能码', '见表 18-6；异常时应答为功能码 + 80h'],
        ['8～11', '地址与数量', '地址 2 字节 + 数量 2 字节，均大端'],
        ['12 起', '数据', '读应答为字节计数 + 数据；写请求为要写的数据'],
    ], [56, 96, 305], '表 18-6　Modbus TCP 帧结构')
    S.append(P('驱动用到的功能码：'))
    S += TBL([
        ['功能码', '含义', '驱动的用途'],
        ['01', '读线圈', 'M/Y/S/T/C 等位软元件的读'],
        ['02', '读离散输入', 'X 的读（X 只读，用这个码）'],
        ['03', '读保持寄存器', 'D/TD/CD/SR/HCD/E 等字软元件的读'],
        ['05', '写单线圈', '写一个位'],
        ['06', '写单寄存器', '写一个字'],
        ['15', '写多线圈', '写连续多位'],
        ['16', '写多寄存器', '写连续多字'],
    ], [64, 130, 263], '表 18-7　驱动用到的 Modbus 功能码')
    S.append(P('PLC 拒绝请求时，应答功能码加 80h，随后的异常码转成标签的 IOResult：'))
    S += TBL([
        ['异常码', '驱动返回', '含义'],
        ['01', 'ioIllegalFunction', '功能码非法：例如对 X 发写请求以外的受限操作'],
        ['02', 'ioIllegalRegAddress', '地址非法：超出软元件范围、跨断层未拆分'],
        ['03', 'ioIllegalValue', '数量非法：一帧要的位/字数超过 PLC 允许值'],
        ['04', 'ioPLCError', 'PLC 执行失败'],
        ['05', 'ioAcknowledge', '已受理，稍后完成'],
        ['06', 'ioBusy', 'PLC 忙，稍后重试'],
        ['08', 'ioMemoryParityError', '扩展内存奇偶校验错'],
        ['0A/0B', 'ioCommError', '网关类错误：目标不可达、响应超时'],
        ['其他', 'ioPLCError', '未归类的异常，抓包看原始码'],
    ], [64, 172, 221], '表 18-8　Modbus 异常码与 TProtocolIOResult 的对应')
    S.append(P('表 18-3 与 DeltaDriver 单元里的 DELTA_DEV_* 常量、DeviceAddress 函数一一对应；'
               '表 18-8 与 DeltaTCP 单元 DecodePkg 里的 case 分支一一对应。驱动扩展软元件或'
               '状态码时，同步更新这两张表即可。'))
    S.append(P('驱动随 pascalscada.lpk 一起编译，单元是 DeltaTCP（Modbus TCP 帧编解码）和 '
               'DeltaDriver（地址映射、内存管理、扫描），纯 Pascal 实现，不依赖任何 DLL，'
               '可以编译到 Win32/Win64/Linux 各个平台。地址映射和帧格式有 72 项自测'
               '（tools/deltatest.lpr），改动驱动后跑一遍即可回归。'))

    doc.build(S)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'delta_chapter.pdf'
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 102
    build(out, start)
    print('written', out)
