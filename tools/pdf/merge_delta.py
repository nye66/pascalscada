# -*- coding: utf-8 -*-
"""把第 18 章（台达 PLC）合并进手册并重建书签。可重复执行（每次从备份恢复再合并）。"""
import shutil
import pymupdf

MANUAL = r'D:/lazarus/components/pascalscada最新控件/PascalSCADA中文使用手册.pdf'
BACKUP = r'D:/lazarus/components/pascalscada最新控件/PascalSCADA中文使用手册_含17章备份.pdf'
CHAPTER = r'E:/Pascalscada/tools/pdf/build/delta_chapter.pdf'

# 从备份恢复，保证脚本幂等
shutil.copyfile(BACKUP, MANUAL)

doc = pymupdf.open(MANUAL)
assert doc.page_count == 101, '备份页数异常: %d' % doc.page_count
chap = pymupdf.open(CHAPTER)
assert chap.page_count == 7, '章节页数异常: %d' % chap.page_count

# 追加章节页面
doc.insert_pdf(chap, start_at=doc.page_count)

OLD_TOC = pymupdf.open(BACKUP).get_toc()

NEW_ITEMS = [
    (1, '第 18 章　台达 PLC（Modbus TCP）', 102),
    (2, '18.1 简介', 102),
    (2, '18.2 所需组件', 102),
    (2, '18.3 准备 PLC 与选择系列', 103),
    (2, '18.4 驱动属性', 103),
    (2, '18.5 地址映射', 104),
    (2, '18.6 数据宽度与 32 位数据', 105),
    (2, '18.7 分步示例', 105),
    (2, '18.8 常见问题', 106),
    (2, '18.9 协议参考', 107),
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
