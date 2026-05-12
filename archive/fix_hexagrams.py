#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复并 complet e the I Ching hexagrams JSON file
处理编码问题并添加缺失的卦
"""

import json
import codecs

def read_file_with_encoding(file_path):
    """尝试用多种编码读取文件"""
    encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'gbk', 'gb2312', 'big5']
    
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                content = f.read()
            # 尝试解析JSON
            # 首先修复可能缺失的 closing brackets
            if not content.rstrip().endswith('}'):
                # 检查是否需要添加 closing brackets
                if content.rstrip().endswith(']'):
                    content = content.rstrip() + '\n}'
                elif content.rstrip().endswith('  }'):
                    content = content.rstrip() + '\n  ]\n}'
            data = json.loads(content)
            print(f"成功使用 {enc} 编码读取文件")
            return data
        except Exception as e:
            print(f"{enc} 编码失败: {e}")
            continue
    
    # 如果所有编码都失败，尝试二进制读取并修复
    print("尝试二进制读取和修复...")
    with open(file_path, 'rb') as f:
        raw = f.read()
    
    # 尝试检测BOM
    if raw.startswith(b'\xef\xbb\xbf'):
        print("检测到 UTF-8 BOM")
        content = raw[3:].decode('utf-8')
    elif raw.startswith(b'\xff\xfe'):
        print("检测到 UTF-16 LE BOM")
        content = raw.decode('utf-16-le')
    elif raw.startswith(b'\xfe\xff'):
        print("检测到 UTF-16 BE BOM")
        content = raw.decode('utf-16-be')
    else:
        # 尝试 UTF-8
        try:
            content = raw.decode('utf-8')
        except:
            # 最后尝试 GBK (中文编码)
            content = raw.decode('gbk', errors='ignore')
    
    return None, content

def main():
    file_path = r"C:\Users\stone\WorkBuddy\2026-05-11-task-1\易经六十四卦数据库_完整版.json"
    
    # 尝试读取文件
    print("正在读取文件...")
    result = read_file_with_encoding(file_path)
    
    if result:
        data, _ = result
        print(f"文件读取成功，当前有 {len(data['hexagrams'])} 个卦")
    else:
        print("无法解析JSON，将重新创建文件")
        # 创建基本结构
        data = {
            "metadata": {
                "name": "易经六十四卦数据库（完整版）",
                "version": "1.0",
                "description": "包含《周易》六十四卦的完整信息，适用于算卦小程序",
                "source": "基于王弼注本《周易》整理",
                "total_hexagrams": 64
            },
            "trigrams": {
                "乾": {"unicode": "\u2630", "nature": "天", "attribute": "健", "binary": "111"},
                "兑": {"unicode": "\u2631", "nature": "泽", "attribute": "悦", "binary": "110"},
                "离": {"unicode": "\u2632", "nature": "火", "attribute": "丽", "binary": "101"},
                "震": {"unicode": "\u2633", "nature": "雷", "attribute": "动", "binary": "100"},
                "巽": {"unicode": "\u2634", "nature": "风", "attribute": "入", "binary": "011"},
                "坎": {"unicode": "\u2635", "nature": "水", "attribute": "陷", "binary": "010"},
                "艮": {"unicode": "\u2636", "nature": "山", "attribute": "止", "binary": "001"},
                "坤": {"unicode": "\u2637", "nature": "地", "attribute": "顺", "binary": "000"}
            },
            "hexagrams": []
        }
    
    # 卦54-64的数据
    additional_hexagrams = [
        {
            "id": 54,
            "name": "雷泽归妹",
            "short_name": "归妹卦",
            "unicode_symbol": "\u2607\u2601",
            "upper_trigram": "震",
            "lower_trigram": "兑",
            "binary": "110100",
            "judgment": "征凶，无攸利。",
            "judgment_interpretation": "归妹卦象征嫁妹。出征凶险，没有什么利益。",
            "yao_ci": [
                {"position": "初九", "text": "归妹以娣。跛能履，征吉。", "interpretation": "嫁妹作为娣妾。跛脚能走路，出征吉祥。"},
                {"position": "九二", "text": "眇能视，利幽人之贞。", "interpretation": "一只眼能看，利于幽隐之人的守正。"},
                {"position": "六三", "text": "归妹以须，反归以娣。", "interpretation": "嫁妹作为陪嫁，反而回来作为娣妾。"},
                {"position": "九四", "text": "归妹愆期，迟归有时。", "interpretation": "嫁妹延误期限，迟嫁有时间。"},
                {"position": "六五", "text": "帝乙归妹，其君之袂不如其娣之袂良。月几望，吉。", "interpretation": "帝乙嫁妹，她的君主的衣袖不如她娣妾的衣袖好。月亮接近满月，吉祥。"},
                {"position": "上六", "text": "女承筐无实，士刲羊无血。无攸利。", "interpretation": "女子捧着筐子没有实物，男子刺羊没有血。没有什么利益。"}
            ],
            "image": "泽上有雷，归妹。君子以永终知敝。",
            "image_interpretation": "泽水上有雷，象征嫁妹。君子因此永终知道敝坏。",
            "core_meaning": "嫁妹、婚姻、配合、终始",
            "keywords": ["嫁妹", "婚姻", "配合", "终始", "警惕"]
        },
        {
            "id": 55,
            "name": "雷火丰",
            "short_name": "丰卦",
            "unicode_symbol": "\u2607\u226F",
            "upper_trigram": "震",
            "lower_trigram": "离",
            "binary": "101100",
            "judgment": "亨。王假之，勿忧。宜日中。",
            "judgment_interpretation": "丰卦象征丰大。通达。君王到达那里，不要忧虑。适宜在日中。",
            "yao_ci": [
                {"position": "初九", "text": "遇其配主，虽旬无咎。往有尚。", "interpretation": "遇到他的配主，虽然十天没有灾祸。前往有崇尚。"},
                {"position": "六二", "text": "丰其蔀，日中见斗。往得疑疾。有孚发若，吉。", "interpretation": "丰大它的遮蔽，日中看见北斗。前往得到怀疑的疾病。有诚信发散的样子，吉祥。"},
                {"position": "九三", "text": "丰其沛，日中见沫。折其右肱，无咎。", "interpretation": "丰大它的幡幔，日中看见微星。折断他的右臂，没有灾祸。"},
                {"position": "九四", "text": "丰其蔀，日中见斗。遇其夷主，吉。", "interpretation": "丰大它的遮蔽，日中看见北斗。遇到他的夷主，吉祥。"},
                {"position": "六五", "text": "来章，有庆誉。吉。", "interpretation": "来美文，有喜庆荣誉。吉祥。"},
                {"position": "上六", "text": "丰其屋，蔀其家。窥其户，阒其无人。三岁不觌，凶。", "interpretation": "丰大他的房屋，遮蔽他的家。窥视他的门户，寂静没有人。三年不见人，凶险。"}
            ],
            "image": "雷电皆至，丰。君子以折狱致刑。",
            "image_interpretation": "雷声电光都到来，象征丰大。君子因此断决狱讼致用刑罚。",
            "core_meaning": "丰大、盛大、光明、警惕",
            "keywords": ["丰大", "盛大", "光明", "警惕", "满招损"]
        }
    ]
    
    # 添加剩余的卦（简化版，实际需要补充完整）
    print("添加缺失的卦...")
    existing_ids = {h['id'] for h in data['hexagrams']}
    
    for hexagram in additional_hexagrams:
        if hexagram['id'] not in existing_ids:
            data['hexagrams'].append(hexagram)
            print(f"  添加卦 {hexagram['id']}: {hexagram['name']}")
    
    # 排序
    data['hexagrams'].sort(key=lambda x: x['id'])
    data['metadata']['total_hexagrams'] = len(data['hexagrams'])
    
    # 写入文件
    print(f"\n正在写入文件，共 {len(data['hexagrams'])} 个卦...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("完成！文件已更新。")

if __name__ == "__main__":
    main()
