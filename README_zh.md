# xingrong-to-anki

*[English](README.md) | [中文](README_zh.md)*

将星荣英语课程 PDF 转换为 Anki 闪卡，支持自动词汇提取和统一卡组生成。

## 项目简介

本项目可以将星荣英语课程的 PDF 文件转换为单个统一的 Anki 卡组，所有词汇卡片按课程标签组织。非常适合系统性的中英文词汇学习。

## 功能特色

- 🔄 **批量 PDF 处理**：一次处理所有课程 PDF
- 🏷️ **统一卡组标签**：单个卡组，用课程标签组织
- 🇨🇳🇺🇸 **中英文卡片**：正面（中文）→ 背面（英文 + 音标）
- 📖 **智能内容提取**：从第二页开始自动识别词汇内容
- 🔍 **重复检测**：自动去除跨课程的重复词汇
- 🐳 **开发容器支持**：一键式开发环境
- 🎯 **Anki 优化**：直接导入 `.apkg` 文件，格式完美

## 环境要求

### 使用开发容器（推荐）

1. 在 VS Code 中打开项目（需安装 DevContainer 扩展）
2. VS Code 会自动检测 `.devcontainer/devcontainer.json` 并提示在容器中重新打开
3. 容器会自动安装 `requirements.txt` 中的依赖

### 手动安装

1. 安装 Python 3.9+
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### 处理所有 PDF（生成统一卡组）

```bash
python main.py
```

这将：
- 处理 `pdf/` 目录中的所有 PDF 文件
- 生成包含所有词汇卡片的统一卡组
- 使用标签组织课程（如 `Lesson_1`、`Lesson_2` 等）
- 创建一个 `.apkg` 文件：`星荣英语词汇大全.apkg`

### 自定义卡组名称

```bash
python main.py --deck-name "我的英语词汇"
```

### 处理单个 PDF

```bash
python main.py -f "零基础学英语第1课-星荣英语笔记.pdf"
```

### 自定义目录

```bash
python main.py -d my_pdfs -o my_anki_decks
```

### 列出可用的 PDF 文件

```bash
python main.py --list-pdfs
```

## 命令行选项

- `-f, --file`：处理单个 PDF 文件
- `-d, --pdf-dir`：PDF 目录路径（默认：`pdf`）
- `-o, --output-dir`：Anki 卡组输出目录（默认：`anki_decks`）
- `--list-pdfs`：列出所有 PDF 文件并退出
- `--deck-name`：卡组名称（默认：`星荣英语词汇大全`）

## 输出说明

脚本生成可直接导入 Anki 的 `.apkg` 文件：

### 统一卡组
- 创建包含所有课程词汇的单个卡组
- 使用标签按课程组织卡片
- 文件命名：`星荣英语词汇大全.apkg`（或自定义名称）
- 标签组织：
  - 每个课程有独特标签（如 `Lesson_1`、`Lesson_2`、`Lesson_5_5`）
  - 所有卡片都有通用标签：`Xingrong`、`English`、`Vocabulary`
  - 使用 Anki 浏览器按标签筛选，学习特定课程

## 在 Anki 中使用生成的卡组

### 导入卡组
1. 打开 Anki
2. 选择 文件 → 导入
3. 选择生成的 `.apkg` 文件
4. 统一卡组将导入所有词汇卡片

### 使用统一卡组学习
您可以：
1. **混合学习所有卡片**：正常使用卡组进行混合复习
2. **学习特定课程**：
   - 打开 Anki 浏览器（浏览按钮）
   - 使用标签筛选器选择特定课程（如 `Lesson_1`）
   - 为特定课程创建自定义学习会话
3. **按课程跟踪进度**：使用 Anki 统计功能查看每个标签的进度

## 卡片格式

- **正面**：中文文本
- **背面**：英文翻译 + 音标（如有）
- **标签**：课程编号和元数据

## 项目结构

```
xingrong-to-anki/
├── .devcontainer/
│   └── devcontainer.json          # DevContainer 配置
├── .github/
│   └── workflows/
│       └── test.yml                # GitHub Actions 测试
├── pdf/                           # 输入 PDF 文件
├── anki_decks/                    # 生成的 Anki 卡组（自动创建）
├── pdf_parser.py                  # PDF 内容提取
├── anki_generator.py              # Anki 卡组生成  
├── main.py                        # 主脚本
├── test_setup.py                  # 环境验证
├── setup.py                       # Python 包配置
├── requirements.txt               # Python 依赖
├── LICENSE                        # MIT 许可证
├── .gitignore                     # Git 忽略规则
├── README.md                      # 英文说明文档
└── README_zh.md                   # 中文说明文档（本文件）
```

## 开发调试

### 测试单个组件

```bash
# 测试 PDF 解析
python pdf_parser.py

# 测试 Anki 生成
python anki_generator.py

# 验证环境配置
python test_setup.py
```

### 依赖包

- `pdfplumber`：PDF 文本提取
- `genanki`：Anki 卡组生成
- `PyPDF2`：额外的 PDF 处理支持

## 常见问题

### 没有提取到卡片
- 确保 PDF 从第二页开始包含中英文文本
- 检查 PDF 是否有密码保护或损坏
- 运行 `python pdf_parser.py` 验证文本提取

### Anki 导入问题
- 确保 Anki 是最新版本
- 尝试一次导入一个卡组
- 检查 `.apkg` 文件是否损坏

### DevContainer 问题
- 确保 Docker 正在运行
- 检查 VS Code 是否安装了 DevContainer 扩展
- 尝试重建容器：命令面板 → "Dev Containers: Rebuild Container"

## 贡献指南

欢迎贡献代码！请随时提交 Pull Request。

### 开发环境设置

1. Fork 本仓库
2. 克隆你的 fork
3. 在 VS Code 中使用 DevContainer 扩展打开
4. 进行修改
5. 运行 `python test_setup.py` 测试
6. 提交 pull request

### 代码规范

- 遵循代码整洁之道
- 优先使用英文注释
- 编写完善的错误处理

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- 感谢星荣英语教学材料
- 使用 [genanki](https://github.com/kerrickstaley/genanki) 进行 Anki 卡组生成
- 使用 [pdfplumber](https://github.com/jsvine/pdfplumber) 进行 PDF 处理

## 支持

如果这个项目对你有帮助，请给个 ⭐️ 支持一下！

有问题或建议？欢迎提交 [Issue](../../issues)。
