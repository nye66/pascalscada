#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoShop (汇川) HMI 监视变量表 CSV 导入工具
============================================
用途:
  解析 AutoShop "导出 HMI 监视变量表" 生成的 CSV (GBK 编码, '#' 注释头),
  生成:
    1. <out>_变量表.csv  —— UTF-8 干净变量清单 (名称/类型/软元件/地址/周期/注释)
    2. <out>_tags.txt    —— 可直接粘贴的 Pascal 代码, 运行时批量创建
                              TPLCTagNumber 并绑定到协议驱动

地址说明 (重要):
  CSV 中 "UB 21004E0" / "UW 21004F0" 是 H5U 变量区(标签区)的十六进制地址,
  该区域不在 H5U 内置 Modbus (502端口) 编址表内, 需走 12939 端口标签协议
  (TH5UTagTCPDriver)。生成的标签代码使用
  MemReadFunction=H5UTAG_FUNC_UB(1)/H5UTAG_FUNC_UW(17) + MemAddress=十六进制原值
  (驱动属性 WordAddressInBits 保持默认 True), 与 TH5UTagTCPDriver 配套;
  若变量在 PLC 程序中映射到了 D/M, 只需把 MemReadFunction/MemWriteFunction 改为
  对应汇川 Modbus 功能码并填十进制地址即可走 TInovanceTCPDriver (Modbus TCP 502)。

用法:
  python autoshop_import.py <输入.csv> [输出前缀]
"""
import csv, io, os, sys

#: 软元件 -> H5UTagDriver 中的 MemReadFunction 功能码
DEV_FUNC = {'UB': 'H5UTAG_FUNC_UB', 'UW': 'H5UTAG_FUNC_UW'}

TYPE_MAP = {
    'Bool':   'pttDefault',
    'Int16':  'pttSmallInt',
    'UInt16': 'pttWord',
    'Int32':  'pttLongInt',
    'UInt32': 'pttDWord',
    'Float':  'pttFloat',
    'Double': 'pttDouble',
    'Int64':  'pttInt64',
}

def parse_addr(addr_str):
    """'UB 21004E0' -> ('UB', 0x21004E0)"""
    parts = addr_str.strip().split()
    if len(parts) != 2:
        raise ValueError('地址格式不正确: %r' % addr_str)
    dev = parts[0].upper()
    if dev not in ('UB', 'UW'):
        raise ValueError('不支持的软元件前缀: %r' % parts[0])
    return dev, int(parts[1], 16)

def parse_period(p):
    """'100ms' -> 100 (毫秒)"""
    p = p.strip().lower()
    if p.endswith('ms'):
        return int(float(p[:-2]))
    if p.endswith('s'):
        return int(float(p[:-1]) * 1000)
    return int(float(p))

def safe_ident(name, idx):
    """把中文/点分变量名转成 Pascal 标识符"""
    tail = name.split('.')[-1] if '.' in name else name
    out = ''.join(c for c in tail if c.isascii() and (c.isalnum() or c == '_'))
    if not out or not out[0].isalpha():
        out = 'Tag_%03d' % idx
    return out

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    src = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(os.path.basename(src))[0]

    raw = open(src, 'rb').read().decode('gb18030', errors='replace')
    rows = list(csv.reader(io.StringIO(raw)))
    tags = []
    for r in rows:
        if len(r) < 6 or not r[0].strip() or r[0].strip().startswith('#') or r[0] == '名称':
            continue
        name = r[0].strip()
        typ = r[2].strip()
        dev, addr = parse_addr(r[5])
        period = parse_period(r[6]) if len(r) > 6 and r[6].strip() else 100
        comment = r[11].strip() if len(r) > 11 else ''
        tags.append((name, typ, dev, addr, period, comment))

    outdir = os.path.dirname(os.path.abspath(src))
    # 1) 干净变量表
    table_path = os.path.join(outdir, prefix + '_变量表.csv')
    with open(table_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['名称', '类型', '软元件', '地址(HEX)', '地址(DEC)', '采集周期(ms)', '注释'])
        for name, typ, dev, addr, period, comment in tags:
            w.writerow([name, typ, dev, '%08X' % addr, addr, period, comment])

    # 2) Pascal 标签创建代码
    code_path = os.path.join(outdir, prefix + '_tags.txt')
    L = []
    L.append('// 自动生成: AutoShop HMI 监视变量表导入工具 (源: %s)' % os.path.basename(src))
    L.append('// 变量数: %d    生成时间: 见文件日期' % len(tags))
    L.append('// 软元件 UB=变量区位地址  UW=变量区字地址 (十六进制)')
    L.append('// ADriver 传入协议驱动组件 (TH5UTagTCPDriver); 若走 Modbus 502 请改 MemReadFunction/WriteFunction')
    L.append('')
    L.append('procedure AddAutoShopTags(AOwner: TComponent; ADriver: TProtocolDriver);')
    L.append('var')
    L.append('  t: TPLCTagNumber;')
    L.append('')
    L.append('  function NewTag(const AName: string; AFunc: Cardinal; AAddr: Cardinal;')
    L.append('    AType: TTagType; AUpdate: Cardinal): TPLCTagNumber;')
    L.append('  begin')
    L.append('    Result := TPLCTagNumber.Create(AOwner);')
    L.append('    Result.Name := AName;')
    L.append('    Result.ProtocolDriver := ADriver;')
    L.append('    Result.MemReadFunction := AFunc;')
    L.append('    Result.MemWriteFunction := AFunc;')
    L.append('    Result.MemAddress := AAddr;')
    L.append('    Result.TagType := AType;')
    L.append('    Result.UpdateTime := AUpdate;')
    L.append('    Result.AutoRead := True;')
    L.append('  end;')
    L.append('')
    L.append('begin')
    used = set()
    for i, (name, typ, dev, addr, period, comment) in enumerate(tags, 1):
        ident = safe_ident(name, i)
        base, n = ident, 1
        while ident in used:
            n += 1
            ident = '%s_%d' % (base, n)
        used.add(ident)
        cmt = ' // %s%s' % (name, ('  ' + comment) if comment else '')
        L.append("  t := NewTag('%s', %s, $%08X, %s, %d);%s"
                 % (ident, DEV_FUNC[dev], addr, TYPE_MAP.get(typ, 'pttDefault'),
                    period, cmt))
    L.append('end;')
    with open(code_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))

    print('变量数: %d' % len(tags))
    print('输出: %s' % table_path)
    print('输出: %s' % code_path)

if __name__ == '__main__':
    main()
