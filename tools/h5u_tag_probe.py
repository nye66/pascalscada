#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汇川 H5U 标签通讯（端口 12939）帧格式探测工具
==============================================
用法:
  python h5u_tag_probe.py 192.168.1.10
  python h5u_tag_probe.py 192.168.1.10 --port 12939 --addr 21004F0 --unit 1

作用:
  H5U 的"变量区"（AutoShop 导出的 UB/UW 地址）只在 12939 端口上由汇川私有
  协议提供，官方没有公开帧格式。本工具按"多种候选帧格式"逐个发送一条读
  请求，把 PLC 的真实应答以十六进制打印出来，据此确定帧格式，再把结论填进
  PascalSCADA 的 TH5UTagTCPDriver.FrameFormat（或调整其 Encode/Decode）。

  只发只读请求（读 2 个字），不会修改 PLC 里的任何数据。

判定:
  某候选格式打印出 "RX ..." 有数据且功能码对得上 → 该格式正确。
  全部超时 → 检查 IP/端口/网线，或 PLC 未开启该服务（AutoShop 在线监视能
  连上则说明端口是通的）。
"""
import argparse
import socket
import sys
import time


def build_mbap(unit, fc, addr, count, txid=1):
    """MBAP + 4 字节地址（驱动中的 hffMbapExt）"""
    pdu = bytes([fc]) + addr.to_bytes(4, 'big') + count.to_bytes(2, 'big')
    header = txid.to_bytes(2, 'big') + b'\x00\x00' + (len(pdu) + 1).to_bytes(2, 'big') + bytes([unit])
    return header + pdu


def build_hz(unit, fc, addr, count, seq=1):
    """48 5A 帧头变体（驱动中的 hffHzExt）"""
    pdu = bytes([fc]) + addr.to_bytes(4, 'big') + count.to_bytes(2, 'big')
    header = b'\x48\x5A' + seq.to_bytes(2, 'big') + b'\x00\x00\x00\x00' + len(pdu).to_bytes(2, 'big')
    return header + pdu


def build_mbap_modbus(unit, fc, addr, count, txid=1):
    """标准 Modbus TCP（2 字节地址）——用于对照，确认 12939 是否直接说 Modbus"""
    pdu = bytes([fc]) + (addr & 0xFFFF).to_bytes(2, 'big') + count.to_bytes(2, 'big')
    header = txid.to_bytes(2, 'big') + b'\x00\x00' + (len(pdu) + 1).to_bytes(2, 'big') + bytes([unit])
    return header + pdu


def hexs(b):
    return ' '.join('%02X' % x for x in b) if b else '(空)'


def try_frame(name, frame, host, port, timeout):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
    except OSError as e:
        print('%-28s 连接失败: %s' % (name, e))
        s.close()
        return False, b''
    got = b''
    try:
        # 有些设备连接后会先发一段握手/问候数据
        try:
            banner = s.recv(256)
            if banner:
                print('%-28s 连接后主动发来: %s' % (name, hexs(banner)))
        except socket.timeout:
            pass
        print('%-28s TX %s' % (name, hexs(frame)))
        s.sendall(frame)
        time.sleep(0.05)
        try:
            got = s.recv(512)
        except socket.timeout:
            got = b''
        print('%-28s RX %s' % (name, hexs(got)))
    finally:
        s.close()
    return bool(got), got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('host', help='PLC 的 IP 地址')
    ap.add_argument('--port', type=int, default=12939)
    ap.add_argument('--addr', default='21004F0', help='变量区地址（十六进制，默认取 CSV 里的第一个 UW）')
    ap.add_argument('--unit', type=int, default=1, help='站号，IT7000 默认 1')
    ap.add_argument('--timeout', type=float, default=1.0)
    args = ap.parse_args()

    try:
        addr = int(args.addr, 16)
    except ValueError:
        print('地址必须是十六进制，例如 21004F0')
        sys.exit(1)

    print('目标 %s:%d  地址 UW %08X  站号 %d\n' % (args.host, args.port, addr, args.unit))

    candidates = [
        ('hffMbapExt  读2字 fc03', build_mbap(args.unit, 3, addr, 2)),
        ('hffHzExt    读2字 fc03', build_hz(args.unit, 3, addr, 2)),
        ('Modbus TCP  读2字 fc03', build_mbap_modbus(args.unit, 3, addr, 2)),
        ('hffMbapExt  读2字 fc04', build_mbap(args.unit, 4, addr, 2)),
        ('hffHzExt    读2字 fc04', build_hz(args.unit, 4, addr, 2)),
    ]

    answered = []
    for name, frame in candidates:
        ok, data = try_frame(name, frame, args.host, args.port, args.timeout)
        if ok:
            answered.append((name, data))
        time.sleep(0.2)

    print()
    if not answered:
        print('结论: 全部超时/无应答。请确认：')
        print('  1) PLC IP 与端口 12939 可达（AutoShop 能在线监视说明可达）')
        print('  2) 该变量在 PLC 里已下载且地址对应（CSV 是编译后导出的才有效）')
        print('  3) 用 Wireshark 抓 tcp.port==12939，把 pcap 交给驱动作者对齐帧格式')
        return

    print('结论: 以下格式收到了应答，优先试第一个:')
    for name, data in answered:
        print('  - %-22s 应答 %d 字节: %s' % (name, len(data), hexs(data[:32])))
    print()
    print('把上面的应答报文发回来，即可确定 EncodePkg/DecodePkg 的确切布局。')


if __name__ == '__main__':
    main()
