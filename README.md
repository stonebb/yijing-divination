# 易经算卦 (Yijing Divination) v1.0.0

基于《周易》六十四卦的算卦应用，支持 **命令行** 和 **Web 界面** 两种使用方式。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# Web 界面（推荐）
python web/app.py
# 浏览器打开 http://localhost:5000

# 命令行
python main.py -q "我最近的事业运势如何？"
```

## 功能

### 🪙 三种起卦方法

| 方法 | 说明 |
|------|------|
| **铜钱法** | 模拟三枚铜钱投掷六次，最传统的起卦方式 |
| **数字法** | 随机生成六爻，快捷现代 |
| **时间法** | 以当前年月日时起卦，梅花易数 |

### 📊 功能特性

- **六十四卦完整数据库** — 卦辞、象辞、爻辞、释义、关键词
- **本卦 + 变卦** — 动爻自动推导变卦，完整解读
- **Web 可视化界面** — 铜钱投掷动画、卦象卡片、搜索浏览
- **命令行模式** — 支持交互式和非交互式

## 命令行用法

```bash
# 交互式算卦
python main.py

# 直接提问
python main.py -q "财运如何？"

# 指定起卦方法
python main.py -m time -q "感情运势"

# 简要模式
python main.py -q "事业发展" --simple

# 列出全部六十四卦
python main.py -l

# 搜索卦象
python main.py -s 变革

# 查看指定卦详情
python main.py -n 地山谦

# 纯ASCII模式（无Unicode符号）
python main.py --ascii

# 固定随机种子（可复现结果）
python main.py --seed 42
```

## Web 界面

启动后访问 `http://localhost:5000`：

- **起卦占卜** — 输入问题 → 选择方法 → 点击起卦 → 查看完整解读
- **六十四卦浏览** — 搜索、点击查看任意卦象详情

## 项目结构

```
├── main.py              # CLI 命令行入口
├── web/                 # Web 应用
│   ├── app.py           #   Flask API 后端
│   ├── templates/       #   HTML 模板
│   └── static/          #   CSS + JS
├── yijing/              # 核心引擎
│   ├── database.py      #   六十四卦数据库
│   ├── divination.py    #   起卦引擎
│   └── interpreter.py   #   解卦输出
├── data/                # 数据
│   └── hexagrams_db.json
├── tests/               # 测试 (43个)
├── templates/           # 提示词模板
└── requirements.txt
```

## 运行测试

```bash
pytest tests/ -v
```

## 技术栈

- **后端**：Python 3.12 + Flask
- **前端**：原生 HTML/CSS/JS（现代简约风）
- **数据**：JSON 数据库，64卦完整信息

## License

MIT
