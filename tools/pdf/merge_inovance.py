# -*- coding: utf-8 -*-
"""把第 19 章（汇川 PLC）合并进手册并重建书签。可重复执行（每次从备份恢复再合并）。"""
import shutil
import pymupdf

MANUAL = r'D:/lazarus/components/pascalscada最新控件/PascalSCADA中文使用手册.pdf'
BACKUP = r'D:/lazarus/components/pascalscada最新控件/PascalSCADA中文使用手册_含18章备份.pdf'
CHAPTER = r'E:/Pascalscada/tools/pdf/build/inovance_chapter.pdf'

# 从备份恢复，保证脚本幂等
shutil.copyfile(BACKUP, MANUAL)

doc = pymupdf.open(MANUAL)
assert doc.page_count == 108, '备份页数异常: %d' % doc.page_count
chap = pymupdf.open(CHAPTER)
assert chap.page_count == 6, '章节页数异常: %d' % chap.page_count

# 追加章节页面
doc.insert_pdf(chap, start_at=doc.page_count)

OLD_TOC = pymupdf.open(BACKUP).get_toc()

NEW_ITEMS = [
    (1, '第 19 章　汇川 PLC（Modbus TCP）', 109),
    (2, '19.1 简介', 109),
    (2, '19.2 所需组件', 109),
    (2, '19.3 准备 PLC 与选择系列', 110),
    (2, '19.4 驱动属性', 110),
    (2, '19.5 地址映射', 110),
    (2, '19.6 数据宽度与 32 位数据', 111),
    (2, '19.7 分步示例', 112),
    (2, '19.8 常见问题', 113),
    (2, '19.9 协议参考', 114),
]

toc = OLD_TOC + NEW_ITEMS
# 章标题排在同页小节之前
toc.sort(key=lambda e: (e[2], 0 if e[0] == 1 else 1, e[1]))
doc.set_toc(toc)
OUT = MANUAL + '.tmp'
doc.save(OUT, deflate=True, garbage=3)
doc.close()
shutil.move(OUT, MANUAL)

d = pymupdf.open(MANUAL)
print('pages:', d.page_count, 'toc:', len(d.get_toc()))
for e in d.get_toc()[-11:]:
    print(e)
d.close()
