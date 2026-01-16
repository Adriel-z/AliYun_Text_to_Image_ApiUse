# 阿里云百炼图像生成程序使用文档

# 概述

本程序是基于阿里云百炼平台API开发的图像生成工具，使用qwen-image-max多模态模型，支持根据文本描述生成高质量图像。程序采用模块化设计，配置简单，使用方便。

# 环境要求

- Python 3.7 或更高版本

- 网络连接（用于调用阿里云API）

- 有效的阿里云百炼平台API密钥

# 安装步骤

## 1. 克隆或下载程序文件

下载以下四个文件到同一目录：

- config.json - 配置文件

- image_generator.py - 主程序

- prompt.txt - 提示词配置文件

- requirements.txt - 依赖库列表

## 2. 安装Python依赖

```bash

pip install -r requirements.txt
```

或者直接安装所需库：

```bash

pip install requests>=2.28.0
```

## 3. 配置API密钥

1. 访问阿里云百炼平台

2. 注册并登录账号

3. 在控制台获取API密钥（以sk-开头）

4. 编辑config.json文件，将API密钥填入相应位置：

```json

{
    "DASHSCOPE_API_KEY": "sk-你的实际api密钥",
    "MODEL": "qwen-image-max"
}
```

# 配置文件说明

## config.json

```json

{
    "DASHSCOPE_API_KEY": "sk-xxxxxxxxxxxxxxxxxxxxxxxx",  // 必填：你的API密钥
    "MODEL": "qwen-image-max"  // 模型名称，目前固定为qwen-image-max
}
```

## prompt.txt

```txt

# 图像生成参数配置
# 用户只需编辑这个文件即可
prompt:
一个可爱的小猫咪，在花园里玩耍，阳光明媚，花朵盛开
size=1664*928
prompt_extend=true
watermark=false
# 可选：负面提示词（不要出现的内容）
negative_prompt:
低分辨率，多肢体，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感。构图混乱。文字模糊，扭曲。
```

## prompt.txt参数详解

- **prompt段落（必需）**

    - 描述你想要生成的图像内容

    - 支持中英文，建议详细描述主体、环境、风格等

- **size参数**

    - 格式：size=宽度*高度

    - 示例：size=1024*1024、size=1664*928

    - 支持的分辨率：1024*1024、720*1280、1280*720、1664*928、928*1664

- **prompt_extend参数**

    - true：让模型自动优化和扩展你的提示词

    - false：严格使用你提供的提示词

    - 默认：true

- **watermark参数**

    - true：在图片右下角添加百炼水印

    - false：不添加水印

    - 默认：false

- **negative_prompt段落（可选）**

    - 描述你不希望在图像中出现的内容

    - 有助于避免常见AI绘画问题

# 使用方法

## 基本使用

1. 编辑prompt.txt文件，设置你想要生成的图像描述

2. 在命令行中运行程序：

```bash

python image_generator.py
```

程序会自动：

- 读取配置文件

- 调用阿里云API生成图像

- 将生成的图像保存到./output目录

## 输出文件

生成的图像将保存在./output目录中，文件名格式为：

```text

YYYYMMDD_HHMMSS_描述关键词_序号.png
```

例如：

```text

20240115_143022_一个可爱的小猫咪_0.png
```

## 高级选项

### 查看详细日志

在image_generator.py文件中，取消注释以下行可以查看更多调试信息：

```python

# logging.getLogger().setLevel(logging.DEBUG)
```

### 自定义输出目录

修改image_generator.py中的FileManager初始化：

```python

file_manager = FileManager('./custom_output_directory')
```

# 故障排除

## 常见问题及解决方案

### 1. API密钥错误

```text

错误信息：API请求失败，状态码: 401
```

- 检查config.json中的API密钥是否正确

- 确认API密钥以sk-开头

- 在阿里云控制台确认API密钥是否有效且有足够余额

### 2. 网络连接问题

```text

错误信息：网络请求失败
```

- 检查网络连接

- 确认防火墙未阻止程序访问互联网

- 尝试使用代理（如需要）

### 3. 提示词格式错误

```text

错误信息：prompt.txt中未找到有效的prompt内容
```

- 检查prompt.txt文件格式是否正确

- 确认prompt:段落后有内容

- 确保文件编码为UTF-8

### 4. 图片尺寸不支持

```text

错误信息：无效的图片尺寸
```

- 检查size参数格式是否为宽度*高度

- 确认使用支持的分辨率

## 调试建议

- 启用DEBUG日志级别查看详细请求和响应

- 检查output目录是否有写入权限

- 简化prompt测试基本功能

- 确认Python版本为3.7+

# 费用说明

使用阿里云百炼平台API会产生费用，具体计费标准请参考：

- 阿里云百炼定价页面

- 建议首次使用时先测试少量生成，了解费用情况

# 注意事项

- 遵守法律法规：生成的图像内容需符合中国法律法规和阿里云内容政策

- 版权说明：生成的图像版权归属请参考阿里云平台相关规定

- API调用限制：注意API可能有调用频率限制

- 文件备份：定期备份重要的生成结果

- 敏感内容：避免生成涉及个人隐私、暴力、色情等内容

# 技术细节

## 支持的模型

- qwen-image-max：当前支持的多模态图像生成模型

## API接口

- 使用阿里云DashScope API

- 端点：https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation

- 请求格式完全匹配官方API规范

## 文件结构

```text

项目目录/
├── config.json          # API配置
├── image_generator.py   # 主程序
├── prompt.txt           # 提示词配置
├── requirements.txt     # 依赖库
└── output/              # 生成的图片目录
```

# 更新日志

## v2.0 (当前版本)

- 完全匹配阿里云官方API格式

- 支持qwen-image-max模型

- 改进错误处理和日志记录

- 添加负面提示词支持

- 优化文件命名和保存逻辑

# 获取帮助

- 查看程序运行时的详细错误信息

- 参考阿里云百炼官方文档

- 检查本使用文档的故障排除部分

# 免责声明

本程序为开源工具，开发者不对以下情况负责：

- API服务可用性和稳定性

- 生成图像的内容和质量

- 因使用本程序产生的任何直接或间接损失

- 用户违反阿里云服务条款的行为

请在使用前仔细阅读阿里云百炼平台的相关服务协议。
> （注：文档部分内容可能由 AI 生成）