# Handwrite

将普通文本渲染成接近真实手写效果的图片，适合需要手写风格文档、评语、信件等场景。

本项目基于 [handright](https://github.com/Gsllchb/handright) 生成手写体，并通过超采样渲染与后处理，输出适合打印的 A4 尺寸 PNG 图片。

## 功能

- 将中文/英文文本转换为手写风格图片
- 支持多种手写字体，可批量生成不同风格
- 多进程并发渲染，多个字体可同时处理
- 6 倍超采样 + 缩放，提升笔画清晰度
- 自动分页，长文本会拆成多页
- 输出 300 DPI 等效 A4 尺寸（2480 × 3508 像素）

## 项目结构

```
handwrite/
├── handwrite.py    # 主程序
├── fonts/          # 手写字体文件（.ttf）
├── output/         # 生成的图片输出目录
└── README.md
```

## 环境要求

- Python 3.8+
- 依赖库：
  - `handright`
  - `Pillow`

安装依赖：

```bash
pip install handright Pillow
```

## 使用方法

1. 将手写字体文件放入 `fonts/` 目录（例如 `fonts/1.ttf`）。
2. 编辑 `handwrite.py` 底部的配置区：
   - `contents`：要渲染的文本内容
   - `font_files`：要使用的字体列表
3. 运行：

```bash
python handwrite.py
```

4. 在 `output/` 目录查看生成的 PNG 文件，命名格式为 `handwriting_v{字体序号}_style_{页码}.png`。

## 配置说明

### 文本内容

建议使用 `inspect.cleandoc()` 包裹多行字符串，避免 Python 缩进被写入正文：

```python
contents = [
    inspect.cleandoc("""
        收件人：
        正文第一段内容...
        正文第二段内容...
    """)
]
```

注意：多行文本中各行缩进应保持一致，否则 `cleandoc` 可能残留多余空格。若需要中文段落首行缩进两个汉字，请使用全角空格 `　　`，而不是半角空格。

### 字体选择

在 `font_files` 中列出要使用的字体路径，取消注释即可启用多个字体：

```python
font_files = [
    "fonts/1.ttf",
    "fonts/2.ttf",
]
```

### 渲染参数

可在 `generate_handwriting()` 中调整：

- `upscale_factor`：超采样倍数，越大越清晰，但内存占用也更高
- `font` / `line_spacing` / 边距：页面排版
- `perturb_*_sigma`：笔画抖动、字距随机等，影响手写自然度

## 输出示例

运行后会在 `output/` 生成类似以下文件：

```
output/handwriting_v0_style_0.png
output/handwriting_v0_style_1.png
```

若文本较长，会自动分页，每页对应一个 `_style_{页码}` 文件。

## 注意事项

- 渲染高分辨率图片时内存占用较大，建议根据机器配置调整 `upscale_factor`。
- 字体文件体积可能较大，请确保 `fonts/` 目录中有对应文件。
- 当前 PDF 导出功能在代码中预留但未默认启用；如需 PDF，可取消 `pdf_pages.append(final_page)` 的注释。
