# -*- coding: utf-8 -*-
"""把第 20 章（汇川 H5U 标签通讯）合并进手册并重建书签。可重复执行（每次从备份恢复再合并）。"""
import shutil
import pymupdf

MANUAL = r'D:/lazarus/components/pascalscada最新控件/PascalSCADA中文使用手册.pdf'
BACKUP = r'D:/lazarus/components/pascalscada最新控件/PascalSCADA中文使用手册_含19章备份.pdf'
CHAPTER = r'E:/Pascalscada/tools/pdf/build/h5utag_chapter.pdf'

# 先做一份"含 19 章"的备份（幂等：已存在且页数对就不重做）
import os
if not os.path.exists(BACKUP):
    shutil.copyfile(MANUAL, BACKUP)
    print('backup created:', BACKUP)

# 从备份恢复，保证脚本幂等
shutil.copyfile(BACKUP, MANUAL)

doc = pymupdf.open(MANUAL)
assert doc.page_count == 114, '备份页数异常: %d' % doc.page_count
chap = pymupdf.open(CHAPTER)
assert chap.page_count == 8, '章节页数异常: %d' % chap.page_count

# 追加章节页面
doc.insert_pdf(chap, start_at=doc.page_count)

OLD_TOC = pymupdf.open(BACKUP).get_toc()

NEW_ITEMS = [
    (1, '第 20 章　汇川 H5U 标签通讯（12939）', 115),
    (2, '20.1 简介', 115),
    (2, '20.2 变量区与 Modbus 软元件的区别', 115),
    (2, '20.3 所需组件', 115),
    (2, '20.4 从 AutoShop 导入变量表', 116),
    (2, '20.5 驱动属性', 117),
    (2, '20.6 标签地址与数据宽度', 118),
    (2, '20.7 分步示例', 118),
    (2, '20.8 标定帧格式（上线前必做）', 120),
    (2, '20.9 常见问题', 121),
    (2, '20.10 协议参考', 122),
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
for e in d.get_toc()[-12:]:
    print(e)
d.close()
