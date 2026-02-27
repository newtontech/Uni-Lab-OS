#!/usr/bin/env python3
"""
编译 PO 文件为 MO 文件的脚本

使用方法:
    python compile_translations.py
"""

import os
import subprocess
import sys


def compile_po_files():
    """编译所有 PO 文件为 MO 文件"""
    locale_dir = os.path.join(os.path.dirname(__file__), "locales")
    
    for lang in ["en_US", "zh_CN"]:
        po_path = os.path.join(locale_dir, lang, "LC_MESSAGES", "messages.po")
        mo_path = os.path.join(locale_dir, lang, "LC_MESSAGES", "messages.mo")
        
        if not os.path.exists(po_path):
            print(f"Warning: PO file not found: {po_path}")
            continue
        
        # 尝试使用 msgfmt
        try:
            subprocess.run(
                ["msgfmt", "-o", mo_path, po_path],
                check=True,
                capture_output=True
            )
            print(f"✓ Compiled {lang}/messages.po -> messages.mo")
        except (subprocess.CalledProcessError, FileNotFoundError):
            # msgfmt 不可用，使用纯 Python 实现
            try:
                compile_po_to_mo_python(po_path, mo_path)
                print(f"✓ Compiled {lang}/messages.po -> messages.mo (using Python)")
            except Exception as e:
                print(f"✗ Failed to compile {lang}: {e}")


def compile_po_to_mo_python(po_path: str, mo_path: str):
    """
    使用纯 Python 将 PO 文件编译为 MO 文件
    
    MO 文件格式参考: https://www.gnu.org/software/gettext/manual/html_node/MO-Files.html
    """
    import struct
    import re
    
    # 解析 PO 文件
    translations = []
    
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 msgid/msgstr 对
    # 支持多行字符串
    pattern = r'msgid\s+((?:"[^"]*"\s*)+)\s+msgstr\s+((?:"[^"]*"\s*)+)'
    matches = re.findall(pattern, content)
    
    for msgid_part, msgstr_part in matches:
        # 合并多行字符串
        msgid = ''.join(re.findall(r'"([^"]*)"', msgid_part))
        msgstr = ''.join(re.findall(r'"([^"]*)"', msgstr_part))
        
        if msgid and msgstr:  # 只保存有翻译的
            translations.append((msgid, msgstr))
    
    if not translations:
        print(f"Warning: No translations found in {po_path}")
        return
    
    # 构建 MO 文件
    # MO 文件头格式:
    # - magic number: 0x950412de
    # - version: 0
    # - n: 字符串数量
    # - o: 原文偏移
    # - t: 翻译偏移
    # - hash_table_size: 0 (不使用)
    # - hash_table_offset: 0 (不使用)
    
    n = len(translations)
    
    # 计算偏移
    header_size = 5 * 4  # 5 个 32 位整数
    table_size = n * 8   # 每个字符串条目 8 字节 (长度 + 偏移)
    
    original_offset = 28 + table_size * 2
    translation_offset = original_offset
    
    # 计算每个字符串的位置
    offsets = []
    current_offset = original_offset
    
    for msgid, msgstr in translations:
        offsets.append(current_offset)
        current_offset += len(msgid.encode('utf-8')) + 1  # +1 for null terminator
    
    translation_start = current_offset
    
    for msgid, msgstr in translations:
        offsets.append(current_offset)
        current_offset += len(msgstr.encode('utf-8')) + 1
    
    # 写入 MO 文件
    with open(mo_path, 'wb') as f:
        # 写入头部
        f.write(struct.pack('<I', 0x950412de))  # magic number
        f.write(struct.pack('<I', 0))            # version
        f.write(struct.pack('<I', n))            # nstrings
        f.write(struct.pack('<I', 28))           # orig_table_offset
        f.write(struct.pack('<I', 28 + table_size))  # trans_table_offset
        f.write(struct.pack('<I', 0))            # hash_table_size
        f.write(struct.pack('<I', 0))            # hash_table_offset
        
        # 写入原文表
        for i, (msgid, msgstr) in enumerate(translations):
            f.write(struct.pack('<I', len(msgid.encode('utf-8'))))
            f.write(struct.pack('<I', offsets[i]))
        
        # 写入翻译表
        for i, (msgid, msgstr) in enumerate(translations):
            f.write(struct.pack('<I', len(msgstr.encode('utf-8'))))
            f.write(struct.pack('<I', offsets[n + i]))
        
        # 写入字符串数据
        for msgid, msgstr in translations:
            f.write(msgid.encode('utf-8') + b'\x00')
        
        for msgid, msgstr in translations:
            f.write(msgstr.encode('utf-8') + b'\x00')


if __name__ == "__main__":
    compile_po_files()
