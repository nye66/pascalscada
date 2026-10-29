# -*- coding: utf-8 -*-
"""把第 21 章（矢量图形控件与 SVGChanges）合并进手册并重建书签。可重复执行。"""
import os
import shutil
import pymupdf

MANUAL = r'D:/lazarus/components/pascalscada最新控件/PascalSCADA中文使用手册.pdf'
BACKUP = r'D:/lazarus/components/pascalscada最新控件/PascalSCADA中文使用手册_含20章备份.pdf'
CHAPTER = r'E:/Pascalscada/tools/pdf/build/vector_chapter.pdf'

if not os.path.exists(BACKUP):
    shutil.copyfile(MANUAL, BACKUP)
    print('backup created:', BACKUP)

# 从备份恢复，保证脚本幂等
shutil.copyfile(BACKUP, MANUAL)

doc = pymupdf.open(MANUAL)
assert doc.page_count == 122, '备份页数异常: %d' % doc.page_count
chap = pymupdf.open(CHAPTER)
assert chap.page_count == 4, '章节页数异常: %d' % chap.page_count

doc.insert_pdf(chap, start_at=doc.page_count)

OLD_TOC = pymupdf.open(BACKUP).get_toc()

NEW_ITEMS = [
    (1, '第 21 章　矢量图形控件与 SVGChanges', 123),
    (2, '21.1 简介', 123),
    (2, '21.2 SVGChanges 指令总表', 123),
    (2, '21.3 区间与标签联动', 124),
    (2, '21.4 实例：两位选择开关', 124),
    (2, '21.5 渐变：整体引用与改色标', 125),
    (2, '21.6 显示与缩放', 125),
    (2, '21.7 常见问题', 126),
    (2, '21.8 测试与示例', 126),
]

toc = OLD_TOC + NEW_ITEMS
toc.sort(key=lambda e: (e[2], 0 if e[0] == 1 else 1, e[1]))
doc.set_toc(toc)
OUT = MANUAL + '.tmp'
doc.save(OUT, deflate=True, garbage=3)
doc.close()
shutil.move(OUT, MANUAL)

d = pymupdf.open(MANUAL)
print('pages:', d.page_count, 'toc:', len(d.get_toc()))
for e in d.get_toc()[-10:]:
    print(e)
d.close()
