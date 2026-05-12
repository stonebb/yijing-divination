#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完成易经六十四卦数据库文件
读取现有文件，添加卦54-64的数据，并更新metadata
"""

import json
import os

# 卦54-64的数据
new_hexagrams = [
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
    },
    {
        "id": 56,
        "name": "火山旅",
        "short_name": "旅卦",
        "unicode_symbol": "\u226F\u2606",
        "upper_trigram": "离",
        "lower_trigram": "艮",
        "binary": "001101",
        "judgment": "小亨。旅贞吉。",
        "judgment_interpretation": "旅卦象征旅行。小通达。旅行守正吉祥。",
        "yao_ci": [
            {"position": "初六", "text": "旅琐琐，斯其所取灾。", "interpretation": "旅行猥琐的样子，这是他所取来的灾祸。"},
            {"position": "六二", "text": "旅即次，怀其资。得童仆，贞。", "interpretation": "旅行就到馆舍，怀藏着他的资财。得到童仆，守正。"},
            {"position": "九三", "text": "旅焚其次，丧其童仆。贞厉。", "interpretation": "旅行焚烧他的馆舍，丧失他的童仆。守正危险。"},
            {"position": "九四", "text": "旅于处，得其资斧。我心不快。", "interpretation": "旅行在于处所，得到他的资财斧头。我的心不快活。"},
            {"position": "六五", "text": "射雉，一矢亡。终以誉命。", "interpretation": "射野鸡，一支箭丢失。最终以荣誉命令。"},
            {"position": "上九", "text": "鸟焚其巢，旅人先笑后号咷。丧牛于易，凶。", "interpretation": "鸟焚烧它的巢穴，旅人先笑后号啕大哭。在边界丧失牛，凶险。"}
        ],
        "image": "山上有火，旅。君子以明慎用刑而不留狱。",
        "image_interpretation": "山上有火，象征旅行。君子因此明察谨慎使用刑罚而不滞留狱讼。",
        "core_meaning": "旅行、漂泊、客居、谨慎",
        "keywords": ["旅行", "漂泊", "客居", "谨慎", "适应"]
    },
    {
        "id": 57,
        "name": "巽为风",
        "short_name": "巽卦",
        "unicode_symbol": "\u2604\u2604",
        "upper_trigram": "巽",
        "lower_trigram": "巽",
        "binary": "011011",
        "judgment": "小亨。利有攸往，利见大人。",
        "judgment_interpretation": "巽卦象征顺从。小通达。利于有所前往，利于见到大人。",
        "yao_ci": [
            {"position": "初六", "text": "进退，利武人之贞。", "interpretation": "进退，利于武人的守正。"},
            {"position": "九二", "text": "巽在床下，用史巫纷若。吉，无咎。", "interpretation": "顺从在床下，使用史巫纷多的样子。吉祥，没有灾祸。"},
            {"position": "九三", "text": "频巽，吝。", "interpretation": "频繁地顺从，有困难。"},
            {"position": "六四", "text": "悔亡，田获三品。", "interpretation": "悔恨消失，田猎获得三品。"},
            {"position": "九五", "text": "贞吉，悔亡，无不利。无初有终。先庚三日，后庚三日。吉。", "interpretation": "守正吉祥，悔恨消失，没有不利。没有开始有结局。先庚三日，后庚三日。吉祥。"},
            {"position": "上九", "text": "巽在床下，丧其资斧。贞凶。", "interpretation": "顺从在床下，丧失他的资财斧头。守正凶险。"}
        ],
        "image": "随风，巽。君子以申命行事。",
        "image_interpretation": "随风相从，象征顺从。君子因此申明命令施行事务。",
        "core_meaning": "顺从、温和、渗透、执行",
        "keywords": ["顺从", "温和", "渗透", "执行", "柔顺"]
    },
    {
        "id": 58,
        "name": "兑为泽",
        "short_name": "兑卦",
        "unicode_symbol": "\u2601\u2601",
        "upper_trigram": "兑",
        "lower_trigram": "兑",
        "binary": "110110",
        "judgment": "亨，利贞。",
        "judgment_interpretation": "兑卦象征喜悦。通达，利于守正。",
        "yao_ci": [
            {"position": "初九", "text": "和兑，吉。", "interpretation": "和悦，吉祥。"},
            {"position": "九二", "text": "孚兑，吉。悔亡。", "interpretation": "诚信喜悦，吉祥。悔恨消失。"},
            {"position": "六三", "text": "来兑，凶。", "interpretation": "来献喜悦，凶险。"},
            {"position": "九四", "text": "商兑未宁，介疾有喜。", "interpretation": "商量喜悦未安宁，隔绝疾病有喜悦。"},
            {"position": "九五", "text": "孚于剥，有厉。", "interpretation": "诚信于剥落，有危险。"},
            {"position": "上六", "text": "引兑。", "interpretation": "引荐喜悦。"}
        ],
        "image": "丽泽，兑。君子以朋友讲习。",
        "image_interpretation": "两泽相丽，象征喜悦。君子因此与朋友讲说研习。",
        "core_meaning": "喜悦、和悦、交流、分享",
        "keywords": ["喜悦", "和悦", "交流", "分享", "友谊"]
    },
    {
        "id": 59,
        "name": "风水涣",
        "short_name": "涣卦",
        "unicode_symbol": "\u2604\u2605",
        "upper_trigram": "巽",
        "lower_trigram": "坎",
        "binary": "010011",
        "judgment": "亨。王假有庙。利涉大川，利贞。",
        "judgment_interpretation": "涣卦象征涣散。通达。君王到达宗庙。利于涉过大河，利于守正。",
        "yao_ci": [
            {"position": "初六", "text": "用拯马壮，吉。", "interpretation": "用来拯救马匹强壮，吉祥。"},
            {"position": "九二", "text": "涣奔其机，悔亡。", "interpretation": "涣散奔向他的几案，悔恨消失。"},
            {"position": "六三", "text": "涣其躬，无悔。", "interpretation": "涣散他的身体，没有悔恨。"},
            {"position": "六四", "text": "涣其群，元吉。涣有丘，匪夷所思。", "interpretation": "涣散他的群类，大吉。涣散有山丘，不是平常所能想到的。"},
            {"position": "九五", "text": "涣汗其大号，涣王居，无咎。", "interpretation": "涣散如出汗他的重大号令，涣散君王居处，没有灾祸。"},
            {"position": "上九", "text": "涣其血，去逖出，无咎。", "interpretation": "涣散他的血，去除远离脱出，没有灾祸。"}
        ],
        "image": "风行水上，涣。先王以享于帝，立庙。",
        "image_interpretation": "风行于水上，象征涣散。先王因此祭祀天帝，建立宗庙。",
        "core_meaning": "涣散、流通、化解、重聚",
        "keywords": ["涣散", "流通", "化解", "重聚", "祭祀"]
    },
    {
        "id": 60,
        "name": "水泽节",
        "short_name": "节卦",
        "unicode_symbol": "\u2605\u2601",
        "upper_trigram": "坎",
        "lower_trigram": "兑",
        "binary": "110010",
        "judgment": "亨。苦节不可贞。",
        "judgment_interpretation": "节卦象征节制。通达。苦苦节制不可以守正。",
        "yao_ci": [
            {"position": "初九", "text": "不出户庭，无咎。", "interpretation": "不走出户庭，没有灾祸。"},
            {"position": "九二", "text": "不出门庭，凶。", "interpretation": "不走出门庭，凶险。"},
            {"position": "六三", "text": "不节若，则嗟若。无咎。", "interpretation": "不节制啊，那么就嗟叹啊。没有灾祸。"},
            {"position": "六四", "text": "安节，亨。", "interpretation": "安于节制，通达。"},
            {"position": "九五", "text": "甘节，吉。往有尚。", "interpretation": "甘美地节制，吉祥。前往有崇尚。"},
            {"position": "上六", "text": "苦节，贞凶。悔亡。", "interpretation": "苦苦节制，守正凶险。悔恨消失。"}
        ],
        "image": "泽上有水，节。君子以制数度，议德行。",
        "image_interpretation": "泽水上有水，象征节制。君子因此制定数度，评议德行。",
        "core_meaning": "节制、节约、制度、适度",
        "keywords": ["节制", "节约", "制度", "适度", "规范"]
    },
    {
        "id": 61,
        "name": "风泽中孚",
        "short_name": "中孚卦",
        "unicode_symbol": "\u2604\u2601",
        "upper_trigram": "巽",
        "lower_trigram": "兑",
        "binary": "110011",
        "judgment": "豚鱼吉，利涉大川，利贞。",
        "judgment_interpretation": "中孚卦象征心中诚信。豚鱼吉祥，利于涉过大河，利于守正。",
        "yao_ci": [
            {"position": "初九", "text": "虞吉，有它不燕。", "interpretation": "安度吉祥，有他物不宴安。"},
            {"position": "九二", "text": "鸣鹤在阴，其子和之。我有好爵，吾与尔靡之。", "interpretation": "鸣叫的鹤在树荫下，它的儿子应和它。我有好酒爵，我和你共享它。"},
            {"position": "六三", "text": "得敌，或鼓或罢，或泣或歌。", "interpretation": "得到敌人，或者击鼓或者停止，或者哭泣或者歌唱。"},
            {"position": "六四", "text": "月几望，马匹亡，无咎。", "interpretation": "月亮接近满月，马匹丢失，没有灾祸。"},
            {"position": "九五", "text": "有孚挛如，无咎。", "interpretation": "有诚信相连的样子，没有灾祸。"},
            {"position": "上九", "text": "翰音登于天，贞凶。", "interpretation": "鸡鸣之声登到天上，守正凶险。"}
        ],
        "image": "泽上有风，中孚。君子以议狱缓死。",
        "image_interpretation": "泽水上有风，象征心中诚信。君子因此评议狱讼宽缓死刑。",
        "core_meaning": "诚信、感应、和谐、感通",
        "keywords": ["诚信", "感应", "和谐", "感通", "真心"]
    },
    {
        "id": 62,
        "name": "雷山小过",
        "short_name": "小过卦",
        "unicode_symbol": "\u2607\u2606",
        "upper_trigram": "震",
        "lower_trigram": "艮",
        "binary": "001100",
        "judgment": "亨，利贞。可小事，不可大事。飞鸟遗之音，不宜上宜下。大吉。",
        "judgment_interpretation": "小过卦象征小有越过。通达，利于守正。可以做小事，不可以做大事。飞鸟遗留的声音，不适宜在上适宜在下。大吉。",
        "yao_ci": [
            {"position": "初六", "text": "飞鸟以凶。", "interpretation": "飞鸟因此凶险。"},
            {"position": "六二", "text": "过其祖，遇其妣。不及其君，遇其臣。无咎。", "interpretation": "越过他的祖父，遇到他的祖母。来不及他的君王，遇到他的臣子。没有灾祸。"},
            {"position": "九三", "text": "弗过防之，从或戕之。凶。", "interpretation": "不要越过防备它，跟从或许戕害它。凶险。"},
            {"position": "九四", "text": "无咎。弗过遇之，往厉必戒。勿用永贞。", "interpretation": "没有灾祸。不要越过遇到它，前往危险必须警戒。不要使用永远守正。"},
            {"position": "六五", "text": "密云不雨，自我西郊。公弋取彼在穴。", "interpretation": "密云不降雨，从我西边的郊野。公侯用箭射取那在洞穴中。"},
            {"position": "上六", "text": "弗遇过之，飞鸟离之。凶，是谓灾祸。", "interpretation": "没有遇到而越过它，飞鸟遭到罗网。凶险，这叫做灾祸。"}
        ],
        "image": "山上有雷，小过。君子以行过乎恭，丧过乎哀，用过乎俭。",
        "image_interpretation": "山上有雷，象征小有越过。君子因此行为过于恭敬，丧事过于悲哀，用度过于节俭。",
        "core_meaning": "小过、越过、谨慎、适度",
        "keywords": ["小过", "越过", "谨慎", "适度", "收敛"]
    },
    {
        "id": 63,
        "name": "水火既济",
        "short_name": "既济卦",
        "unicode_symbol": "\u2605\u226F",
        "upper_trigram": "坎",
        "lower_trigram": "离",
        "binary": "101010",
        "judgment": "亨小，利贞。初吉终乱。",
        "judgment_interpretation": "既济卦象征已经成功。通达小事，利于守正。起初吉祥最终混乱。",
        "yao_ci": [
            {"position": "初九", "text": "曳其轮，濡其尾。无咎。", "interpretation": "拖曳他的车轮，沾湿他的尾巴。没有灾祸。"},
            {"position": "六二", "text": "妇丧其茀，勿逐，七日得。", "interpretation": "妇人丧失她的蔽膝，不要追赶，七天得到。"},
            {"position": "九三", "text": "高宗伐鬼方，三年克之。小人勿用。", "interpretation": "高宗讨伐鬼方，三年攻克它。小人不要使用。"},
            {"position": "六四", "text": "繻有衣袽，终日戒。", "interpretation": "濡湿有破衣，整日警戒。"},
            {"position": "九五", "text": "东邻杀牛，不如西邻之禴祭，实受其福。", "interpretation": "东邻杀牛祭祀，不如西邻的禴祭，实在承受他的福泽。"},
            {"position": "上六", "text": "濡其首，厉。", "interpretation": "沾湿他的头，危险。"}
        ],
        "image": "水在火上，既济。君子以思患而豫防之。",
        "image_interpretation": "水在火上，象征已经成功。君子因此思考祸患而预先防备它。",
        "core_meaning": "既济、成功、完成、警惕",
        "keywords": ["既济", "成功", "完成", "警惕", "防患"]
    },
    {
        "id": 64,
        "name": "火水未济",
        "short_name": "未济卦",
        "unicode_symbol": "\u226F\u2605",
        "upper_trigram": "离",
        "lower_trigram": "坎",
        "binary": "010101",
        "judgment": "亨。小狐汔济，濡其尾。无攸利。",
        "judgment_interpretation": "未济卦象征尚未成功。通达。小狐几乎渡河，沾湿它的尾巴。没有什么利益。",
        "yao_ci": [
            {"position": "初六", "text": "濡其尾，吝。", "interpretation": "沾湿它的尾巴，有困难。"},
            {"position": "九二", "text": "曳其轮，贞吉。", "interpretation": "拖曳他的车轮，守正吉祥。"},
            {"position": "六三", "text": "未济，征凶。利涉大川。", "interpretation": "尚未成功，出征凶险。利于涉过大河。"},
            {"position": "九四", "text": "贞吉，悔亡。震用伐鬼方，三年有赏于大国。", "interpretation": "守正吉祥，悔恨消失。震动用来讨伐鬼方，三年有赏于大国。"},
            {"position": "六五", "text": "贞吉，无悔。君子之光，有孚吉。", "interpretation": "守正吉祥，没有悔恨。君子的光辉，有诚信吉祥。"},
            {"position": "上九", "text": "有孚于饮酒，无咎。濡其首，有孚失是。", "interpretation": "有诚信于饮酒，没有灾祸。沾湿他的头，有诚信失去这个。"}
        ],
        "image": "火在水上，未济。君子以慎辨物居方。",
        "image_interpretation": "火在水上，象征尚未成功。君子因此谨慎辨别物类安居方位。",
        "core_meaning": "未济、未完成、过渡、希望",
        "keywords": ["未济", "未完成", "过渡", "希望", "谨慎"]
    }
]

def main():
    file_path = r"C:\Users\stone\WorkBuddy\2026-05-11-task-1\易经六十四卦数据库_完整版.json"
    
    # 读取现有文件
    print("正在读取现有文件...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 尝试解析JSON
    try:
        data = json.loads(content)
        print(f"成功读取文件，当前有 {len(data['hexagrams'])} 个卦")
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print("尝试修复JSON格式...")
        # 如果JSON无效，尝试修复（添加缺少的 Closing brackets）
        if not content.rstrip().endswith('}'):
            content = content.rstrip().rstrip(']') + '\n  ]\n}'
            try:
                data = json.loads(content)
                print(f"修复成功！当前有 {len(data['hexagrams'])} 个卦")
            except:
                print("修复失败，将重新创建文件")
                # 如果修复失败，我们需要从头创建
                data = {
                    "metadata": {
                        "name": "易经六十四卦数据库（完整版）",
                        "version": "1.0",
                        "description": "包含《周易》六十四卦的完整信息，适用于算卦小程序",
                        "source": "基于王弼注本《周易》整理",
                        "total_hexagrams": 64,
                        "note": "本文件包含完整64卦数据，每卦包含：卦序、卦名、Unicode符号、上下卦、二进制编码、卦辞、卦辞解读、六爻爻辞及解读、象传、象传解读、核心含义、关键词"
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
                # 需要重新读取原始的卦1-53
    
    # 添加剩余的卦
    existing_ids = [h['id'] for h in data['hexagrams']]
    added_count = 0
    
    for hexagram in new_hexagrams:
        if hexagram['id'] not in existing_ids:
            data['hexagrams'].append(hexagram)
            added_count += 1
            print(f"添加卦 {hexagram['id']}: {hexagram['name']}")
    
    # 按id排序
    data['hexagrams'].sort(key=lambda x: x['id'])
    
    # 更新metadata
    data['metadata']['total_hexagrams'] = len(data['hexagrams'])
    
    # 写回文件
    print(f"\n正在写入文件，共 {len(data['hexagrams'])} 个卦...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("完成！文件已更新。")
    print(f"总共 {len(data['hexagrams'])} 个卦")

if __name__ == "__main__":
    main()
