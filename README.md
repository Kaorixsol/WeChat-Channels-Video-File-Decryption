# 微信视频号解密工具 / WeChat Channels Video Decryption Tool

<div align="center">

[![GitHub Stars](https://img.shields.io/github/stars/Evil0ctal/WeChat-Channels-Video-File-Decryption?style=flat&logo=github&label=Stars)](https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Evil0ctal/WeChat-Channels-Video-File-Decryption?style=flat&logo=github&label=Forks)](https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/Evil0ctal/WeChat-Channels-Video-File-Decryption?style=flat&logo=github&label=Issues)](https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/Evil0ctal/WeChat-Channels-Video-File-Decryption?style=flat&logo=github&label=PRs)](https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption/pulls)
[![Docker Image CI](https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption/actions/workflows/docker-image.yml)

[![Docker Hub](https://img.shields.io/docker/v/evil0ctal/wechat-decrypt-api?label=Docker%20Hub&logo=docker&color=2496ED)](https://hub.docker.com/r/evil0ctal/wechat-decrypt-api)
[![Docker Pulls](https://img.shields.io/docker/pulls/evil0ctal/wechat-decrypt-api?logo=docker&color=2496ED)](https://hub.docker.com/r/evil0ctal/wechat-decrypt-api)
[![Docker Image Size](https://img.shields.io/docker/image-size/evil0ctal/wechat-decrypt-api/latest?logo=docker&label=Image%20Size)](https://hub.docker.com/r/evil0ctal/wechat-decrypt-api)

[![License](https://img.shields.io/github/license/Evil0ctal/WeChat-Channels-Video-File-Decryption?color=blue)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/Evil0ctal/WeChat-Channels-Video-File-Decryption?color=orange)](https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption/graphs/contributors)
[![Last Commit](https://img.shields.io/github/last-commit/Evil0ctal/WeChat-Channels-Video-File-Decryption?logo=github)](https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption/commits/main)
[![Repo Size](https://img.shields.io/github/repo-size/Evil0ctal/WeChat-Channels-Video-File-Decryption?logo=github)](https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption)
[![Code Size](https://img.shields.io/github/languages/code-size/Evil0ctal/WeChat-Channels-Video-File-Decryption?logo=github)](https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption)
[![Top Language](https://img.shields.io/github/languages/top/Evil0ctal/WeChat-Channels-Video-File-Decryption?logo=javascript&color=yellow)](https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption)

</div>

---

一个完整的微信视频号加密视频解密解决方案，基于逆向工程分析实现。本项目使用微信官方的 WebAssembly (WASM) 模块来生成 Isaac64 PRNG 密钥流，并通过 XOR 运算完成视频解密。

## 📖 项目简介

微信视频号使用 **Isaac64**（Indirection, Shift, Accumulate, Add, and Count）密码学伪随机数生成器对视频文件的前 128 KB 数据进行加密。本项目通过以下方式实现完整的解密流程：

- 🔬 **算法分析**：通过逆向工程分析微信客户端，确认使用 Isaac64 PRNG 算法
- 🧩 **WASM 模块**：直接使用微信官方的 `wasm_video_decode.wasm` 模块，保证 100% 兼容性
- 🔑 **密钥流生成**：基于 API 响应中的 `decode_key` 种子值生成 131,072 字节的密钥流
- 🔄 **关键步骤**：密钥流必须经过 `reverse()` 操作（这是成功解密的关键）
- ⚡ **XOR 解密**：对视频前 128 KB 执行 XOR 运算，还原原始 MP4 数据
- 🎯 **多平台支持**：提供在线网页版、命令行工具、图形界面、RESTful API 四种使用方式

**技术栈：** JavaScript (WASM), Python 3.x, Node.js, tkinter, HTML5, Docker

## ✨ 特性

- ✅ **浏览器内一键解密** - 无需安装任何软件，直接在网页中完成解密
- ✅ **完全本地处理** - 视频数据不离开您的设备，100% 保护隐私
- ✅ **RESTful API 服务** - Docker 容器化部署，支持远程调用和批量处理
- ✅ **本地优先架构** - API 服务内置 WASM 文件，优先使用本地加载（速度更快，离线可用）
- ✅ **智能降级机制** - 本地文件加载失败时自动切换到微信 CDN，确保服务可用性
- ✅ 使用微信官方 WASM 模块（保证 100% 兼容性）
- ✅ 支持完整视频解密（文件大小无限制）
- ✅ 提供四种使用方式：在线网页版、命令行版、图形界面版、API 服务
- ✅ 专业级日志输出 - Hex Dump、MP4 分析、XOR 运算展示
- ✅ 实时进度显示和性能统计
- ✅ 包含示例文件和详细技术文档

## 🚀 快速开始

### 前置要求

- **仅浏览器内解密**：现代浏览器 (Chrome/Edge/Safari/Firefox) - 无需其他依赖
- **Python 工具**：Python 3.x（仅用于 CLI/GUI 工具）
- **API 服务**：Node.js 16+ 或 Docker（仅用于 RESTful API）

### 方式一：在线网页版（⭐ 最推荐 - 零安装）

**完全在浏览器中完成解密，无需安装任何软件！**

#### 🌐 访问在线版本

**GitHub Pages（推荐）：** https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/

或本地启动：
```bash
python3 -m http.server 8888
open http://localhost:8888/index.html
```

#### 📝 使用步骤截图

<img src="screenshots/Index.png" alt="在线解密工具界面" width="600">

**在线工具界面**

**🎬 一键解密模式**（最简单）：

1. **输入 decode_key**
   - 从 API 响应的 `$.data.object_desc.media[0].decode_key` 字段获取
   - 例如：`2136343393`

2. **选择加密视频**
   - 点击上传区域或直接拖放文件
   - 支持任意大小的 MP4 文件
   - ⚠️ 文件不会上传到服务器，完全本地处理

3. **开始解密**
   - 点击 "🚀 开始解密" 按钮
   - 观看实时解密过程和详细日志
   - 查看加密/解密文件头对比、XOR 运算示例

4. **下载解密视频**
   - 点击 "💾 下载解密视频" 保存文件
   - 视频可直接播放

**🔑 仅生成密钥流模式**（配合 Python 工具使用）：

1. 切换到 "仅生成密钥流" 标签
2. 输入 `decode_key` 并点击 "生成密钥流"
3. 点击 "导出密钥流" 下载 `keystream_131072_bytes.txt`
4. 使用 Python CLI/GUI 工具解密视频

#### ✨ 在线版本特色功能

- 📊 **专业级 Hex Dump 显示** - 类似 `xxd` 命令的格式化输出
- 🔍 **MP4 文件头深度分析** - Box Size、Type、Brand 等详细信息
- 📐 **XOR 运算可视化** - 展示每个字节的解密过程
- 📈 **实时进度条** - 显示解密进度和处理速度
- 🔒 **加密前后对比** - 直观展示解密效果
- 💯 **性能统计** - 解密耗时、处理速度等

### 方式二：图形界面（推荐不熟悉命令行的用户）

最简单的使用方式，无需命令行操作：

```bash
python3 decrypt_wechat_video_gui.py
```

在图形界面中：
1. 选择或粘贴密钥流
2. 选择加密视频文件
3. 点击"开始解密"按钮
4. 等待解密完成

### 方式三：命令行（推荐进阶用户和自动化场景）

#### 交互模式（推荐）

```bash
python3 decrypt_wechat_video_cli.py
```

按提示操作即可，支持：
- 从文件加载密钥流
- 直接粘贴十六进制密钥流
- 自动验证和引导

#### 命令行参数模式

```bash
# 使用密钥流文件解密
python3 decrypt_wechat_video_cli.py -i wx_encrypted.mp4 -k keystream_131072_bytes.txt -o wx_decrypted.mp4

# 静默模式（脚本调用）
python3 decrypt_wechat_video_cli.py -i encrypted.mp4 -k keystream.txt -o decrypted.mp4 -q

# 查看帮助
python3 decrypt_wechat_video_cli.py --help
```

### 方式四：RESTful API 服务（推荐批量处理和集成使用）

适合需要远程调用、批量处理或集成到其他系统的场景。

#### 🐳 使用 Docker（推荐）

**方式 A: 使用 Docker Hub 镜像（最简单）**

```bash
# 拉取最新镜像
docker pull evil0ctal/wechat-decrypt-api:latest

# 运行服务
docker run -d \
  --name wechat-decrypt-api \
  -p 3000:3000 \
  --shm-size=2gb \
  evil0ctal/wechat-decrypt-api:latest
```

**方式 B: 使用 Docker Compose 本地构建**

```bash
# 进入 API 服务目录
cd api-service

# 使用 Docker Compose 启动
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 📦 或直接使用 Node.js

```bash
# 进入 API 服务目录
cd api-service

# 安装依赖
npm install

# 启动服务
npm start

# 开发模式（自动重启）
npm run dev
```

#### 📸 API 服务界面

<img src="screenshots/API.png" alt="API 服务交互式文档" width="600">

**API 服务交互式文档页面**

#### 🔌 API 调用示例

**完整解密视频：**
```bash
curl -X POST http://localhost:3000/api/decrypt \
  -F "video=@encrypted.mp4" \
  -F "decode_key=2136343393" \
  -o decrypted.mp4
```

**生成密钥流：**
```bash
curl -X POST http://localhost:3000/api/keystream \
  -H "Content-Type: application/json" \
  -d '{"decode_key": "2136343393"}'
```

**查看完整 API 文档：**
```bash
# 浏览器访问文档页面
open http://localhost:3000

# 或获取 JSON 格式的服务信息
curl http://localhost:3000/api/info
```

#### ✨ API 服务特性

访问 `http://localhost:3000` 将显示一个漂亮的交互式文档页面，包含：

- 🎨 **美观界面** - 渐变色设计、代码高亮、响应式布局
- 📊 **实时状态** - WASM 模块健康检查和服务信息
- 🔌 **完整文档** - 所有 API 端点的详细说明和参数
- 💡 **代码示例** - Python、JavaScript/Node.js 等多种语言
- ⚡ **本地优先** - 内置 WASM 文件，优先使用本地加载（速度更快）
- 🛡️ **智能降级** - 本地文件加载失败时自动切换到微信 CDN
- 🐳 **容器化** - Docker 镜像包含完整 WASM 文件，开箱即用
- 🔒 **离线可用** - 即使没有网络也能正常工作

**Python 调用示例：**
```python
import requests

# 解密视频
url = 'http://localhost:3000/api/decrypt'
files = {'video': open('encrypted.mp4', 'rb')}
data = {'decode_key': '2136343393'}

response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    with open('decrypted.mp4', 'wb') as f:
        f.write(response.content)
    print('✅ 解密成功')
```

📚 详细文档请查看：[api-service/README.md](api-service/README.md)

## 📁 文件说明

```
WeChat-Channels-Video-File-Decryption/
├── index.html                      # 🌐 在线一键解密工具（⭐ 推荐）
├── decrypt_wechat_video_cli.py     # 💻 命令行解密工具
├── decrypt_wechat_video_gui.py     # 🖥️ 图形界面解密工具
├── api-service/                    # 🚀 RESTful API 服务
│   ├── server.js                   #    Express API 服务器
│   ├── worker.html                 #    RPC Worker (浏览器 WASM 执行)
│   ├── docs.html                   #    交互式 API 文档页面
│   ├── wechat_files/               #    内置 WASM 文件（本地优先加载）
│   │   ├── wasm_video_decode.wasm  #    Isaac64 WASM 模块（3.8 MB）
│   │   ├── wasm_video_decode.js    #    WASM 加载器（175 KB）
│   │   └── ...                     #    其他 WASM 相关文件
│   ├── package.json                #    依赖配置
│   ├── Dockerfile                  #    Docker 构建文件
│   ├── docker-compose.yml          #    Docker Compose 配置
│   └── README.md                   #    API 服务文档
├── wx_response.json                # 📋 API 响应示例（包含 decode_key）
├── wx_encrypted.mp4                # 🔒 示例加密文件
├── wx_decrypted.mp4                # ✅ 示例解密文件
├── screenshots/                    # 📸 项目截图
│   ├── Index.png                   #    在线工具截图
│   └── API.png                     #    API 服务文档截图
├── wechat_files/                   # 📦 微信官方 WASM 模块（供 index.html 使用）
│   ├── wasm_video_decode.wasm      #    Isaac64 WASM 模块
│   ├── wasm_video_decode.js        #    WASM 加载器
│   ├── wasm_video_decode_fallback.js #  降级版本
│   ├── worker_release.js           #    Worker 脚本
│   └── wasm_video_decode.wat       #    WASM 文本格式（调试用）
├── LICENSE                         # 📄 MIT 许可证
└── README.md                       # 📖 本文件
```

## 🔑 工作原理

### 加密方式

微信视频号使用 **Isaac64 PRNG** 生成密钥流，然后：

1. 只加密视频的前 **131,072 bytes** (128 KB)
2. 使用 **XOR** 进行加密：`encrypted = original ^ keystream`
3. **关键步骤**：密钥流必须 **reverse()** 后才能使用

### 解密流程

```
decode_key → Isaac64 WASM → 生成密钥流 → Reverse → XOR 解密 → MP4 视频
```

### decode_key 获取

从微信视频号 API 响应中提取：

```json
{
  "data": {
    "object_desc": {
      "media": [{
        "decode_key": "2136343393",  // 这就是解密种子
        "url": "https://...",         // 加密视频下载链接
        "file_size": 14088528
      }]
    }
  }
}
```

**⚠️ 重要提示：**
- 微信接口每次请求都会返回**新的加密文件链接**和**新的 decode_key**
- 即使是同一个视频，每次请求获取的 `url` 和 `decode_key` 都不相同
- **必须确保** `decode_key` 与 `url` 是同一次 API 响应中获取的，否则解密将失败
- 如果解密失败，请重新获取 API 响应，确保使用匹配的 key 和文件

## 📝 使用示例

### 示例 1: 在线网页版一键解密（⭐ 最推荐）

**完整流程演示：**

1. **访问工具**
   ```
   https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
   ```

2. **解密操作**
   - 输入 decode_key: `2136343393`
   - 选择加密视频: `wx_encrypted.mp4` (13.44 MB)
   - 点击 "🚀 开始解密"

3. **查看详细日志**
   ```
   ╔═══════════════════════════════════════════════════════════╗
   ║         微信视频号解密工具 - 完整解密流程                ║
   ╚═══════════════════════════════════════════════════════════╝

   📋 解密配置信息:
      🔑 Decode Key: 2136343393
      📹 输入文件: wx_encrypted.mp4
      📊 文件大小: 13.44 MB (14,088,528 bytes)
      🔒 加密范围: 前 131,072 bytes (128 KB)

   🔒 加密文件头（前 64 字节）:
   00000000  23 76 6a 16 ff 8f fe 1a 1c a6 cd 5f 99 48 46 ab  |#vj........_.HF.|
   00000010  d9 09 4e 78 87 c7 22 45 30 27 14 4f 84 d4 fa 05  |..Nx.."E0'.O....|
   ...

   📐 XOR 运算示例（前 8 字节）:
      [0] 0x23 XOR 0x23 = 0x00 ('')
      [1] 0x76 XOR 0x76 = 0x00 ('')
      [2] 0x6a XOR 0x6a = 0x00 ('')
      [3] 0x16 XOR 0x36 = 0x20 (' ')
      [4] 0xff XOR 0x99 = 0x66 ('f')
      [5] 0x8f XOR 0x74 = 0xfb ('t')
      [6] 0xfe XOR 0x79 = 0x87 ('y')
      [7] 0x1a XOR 0x70 = 0x6a ('p')

   🔓 解密后文件头（前 64 字节）:
   00000000  00 00 00 20 66 74 79 70 69 73 6f 6d 00 00 02 00  |... ftypisom....|
   00000010  69 73 6f 6d 69 73 6f 32 61 76 63 31 6d 70 34 31  |isomiso2avc1mp41|
   ...

   📋 MP4 文件头分析:
      📦 Box Size: 32 bytes (0x20)
      🏷️  Box Type: 'ftyp'
      🎬 Major Brand: 'isom'
      📌 Minor Version: 512
      🔗 Compatible Brands: isom, iso2, avc1, mp41

   🔍 MP4 格式验证:
      ✅ 'ftyp' 签名验证通过 @ 偏移 4
      ✅ 文件格式: MP4 (ISO Base Media)
      ✅ 解密成功！文件可以正常播放

   📊 解密统计:
      📁 原始文件: 14,088,528 bytes
      🔓 解密范围: 131,072 bytes (0.93%)
      ⏱️  总耗时: 12.45 ms
      💾 输出文件: decrypted_video.mp4
   ```

4. **下载视频**
   - 点击 "💾 下载解密视频"
   - 文件名: `decrypted_video.mp4`
   - 可直接播放 ✅

**优势：**
- ✅ 零安装 - 只需浏览器
- ✅ 完全本地 - 数据不离开设备
- ✅ 专业日志 - 深入理解技术原理
- ✅ 支持大文件 - 无大小限制
- ✅ 实时进度 - 清晰的处理状态

### 示例 2: GUI 图形界面（推荐不熟悉命令行的用户）

```bash
# 启动 GUI
python3 decrypt_wechat_video_gui.py
```

在图形界面中：
1. 如果有 `keystream_131072_bytes.txt` 文件，会自动加载
2. 或者点击"选择文件"加载密钥流文件
3. 或者直接粘贴十六进制密钥流到文本框
4. 选择加密视频文件 `wx_encrypted.mp4`
5. 点击"🚀 开始解密"
6. 等待完成后点击"📂 打开文件夹"查看结果

### 示例 3: CLI 交互模式

```bash
python3 decrypt_wechat_video_cli.py
```

按照提示操作：
```
🎬 微信视频号解密工具 - 交互模式
======================================================================

⚠️  未找到密钥流文件: keystream_131072_bytes.txt

请选择输入方式：
1. 输入密钥流文件路径
2. 直接粘贴十六进制密钥流
3. 退出

请选择 (1/2/3): 1
请输入密钥流文件路径: keystream_131072_bytes.txt
✅ 密钥流大小: 131,072 bytes (128.00 KB)

请输入加密视频文件路径: wx_encrypted.mp4

请输入输出文件名 (默认: wx_decrypted.mp4):
```

### 示例 4: CLI 命令行模式（自动化）

```bash
# 基本用法
python3 decrypt_wechat_video_cli.py \
  -i wx_encrypted.mp4 \
  -k keystream_131072_bytes.txt \
  -o wx_decrypted.mp4

# 静默模式（用于脚本）
python3 decrypt_wechat_video_cli.py \
  -i encrypted.mp4 \
  -k keystream.txt \
  -o decrypted.mp4 \
  -q

# 使用十六进制字符串
python3 decrypt_wechat_video_cli.py \
  -i encrypted.mp4 \
  -H "0a1b2c3d4e5f..." \
  -o decrypted.mp4
```

### 示例 5: 解密已提供的测试文件

项目已包含测试文件：
- `wx_encrypted.mp4` (加密文件)
- `wx_response.json` (包含 decode_key: 2136343393)

**使用 GUI:**
```bash
python3 decrypt_wechat_video_gui.py
```

**使用 CLI:**
```bash
python3 decrypt_wechat_video_cli.py
```

### 示例 6: 解密新视频（完整流程）

1. **获取视频信息**
   ```bash
   # 抓包获取 API 响应
   # 提取 decode_key 和视频 URL
   ```

2. **下载加密视频**
   ```bash
   curl -o my_encrypted_video.mp4 "视频URL"
   ```

3. **解密视频**

   **方式 A: 在线一键解密（推荐）**
   ```
   访问: https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/

   1. 输入你的 decode_key
   2. 上传 my_encrypted_video.mp4
   3. 点击 "开始解密"
   4. 下载解密视频
   ```

   **方式 B: 生成密钥流 + Python 工具**
   ```bash
   # 步骤 1: 在线生成并导出密钥流
   # 访问网页，切换到"仅生成密钥流"标签

   # 步骤 2: 使用 Python 工具解密
   python3 decrypt_wechat_video_cli.py \
     -i my_encrypted_video.mp4 \
     -k keystream_131072_bytes.txt \
     -o my_decrypted_video.mp4
   ```

## 🔧 命令行参数说明

### CLI 工具参数

```bash
python3 decrypt_wechat_video_cli.py [OPTIONS]
```

**参数列表:**

| 参数 | 说明 | 示例 |
|------|------|------|
| `-i, --input` | 加密视频文件路径 | `-i wx_encrypted.mp4` |
| `-o, --output` | 输出文件路径 | `-o wx_decrypted.mp4` |
| `-k, --keystream-file` | 密钥流文件路径 | `-k keystream_131072_bytes.txt` |
| `-H, --keystream-hex` | 十六进制密钥流字符串 | `-H "0a1b2c3d..."` |
| `-q, --quiet` | 静默模式 | `-q` |
| `--version` | 显示版本信息 | `--version` |
| `-h, --help` | 显示帮助信息 | `--help` |

**使用技巧:**

- 不带任何参数运行进入交互模式（推荐新手）
- 使用 `-q` 参数进行静默输出，适合脚本调用
- 可以使用 `-H` 直接传入密钥流，无需文件
- 输出文件默认为 `wx_decrypted.mp4`

## 🔍 验证解密

成功解密的视频应该：

✅ 文件类型：`ISO Media, MP4 Base Media v1`
✅ 文件头包含 `ftyp` 签名（offset 4）
✅ 可以正常播放

验证命令：
```bash
file wx_decrypted.mp4
```

应该显示：
```
wx_decrypted.mp4: ISO Media, MP4 Base Media v1 [ISO 14496-12:2003]
```

或使用 `xxd` 查看文件头：
```bash
xxd -l 32 wx_decrypted.mp4
```

应该看到类似：
```
00000000: 0000 0020 6674 7970 6973 6f6d 0000 0200  ... ftypisom....
00000010: 6973 6f6d 6973 6f32 6165 7631 6d70 3431  isomiso2aev1mp41
```

## ⚠️ 重要提示

1. **decode_key 和加密文件必须匹配** ⭐ 最重要
   - 微信接口每次请求都会返回新的加密文件链接和 decode_key
   - 即使是同一个视频，每次请求的 key 和 URL 都不同
   - **必须确保** decode_key 与加密视频文件来自同一次 API 响应
   - 使用不匹配的 key 会导致解密失败

2. **必须使用 reverse() 操作**
   - 密钥流必须反转才能正确解密
   - HTML 页面和 Python 工具已自动处理此步骤

3. **只加密前 128KB**
   - 视频的后续部分未加密
   - 解密脚本会自动处理

## 🛠️ 技术细节

### Isaac64 算法

- **类型**: 密码学安全的伪随机数生成器
- **周期**: 2^8295
- **输出**: 64-bit 随机数
- **实现**: 微信官方 WASM 模块

### 关键代码

**JavaScript (密钥流生成)**:
```javascript
function wasm_isaac_generate(ptr, size) {
    decryptor_array = new Uint8Array(size);
    var wasmArray = new Uint8Array(Module.HEAPU8.buffer, ptr, size);
    decryptor_array.set(wasmArray.reverse());  // ⚠️ 必须反转
}
```

**Python (XOR 解密)**:
```python
# 解密前 131072 字节
for i in range(decrypt_len):
    decrypted[i] = encrypted[i] ^ keystream[i]
```

## 🌐 在线工具详解

### 功能特色

#### 🎬 一键解密模式

完全在浏览器中完成视频解密，无需任何额外软件：

**工作流程：**
```
用户选择文件（本地） → 输入 decode_key
    ↓
浏览器读取文件（不上传）
    ↓
WASM 生成密钥流（Isaac64）
    ↓
JavaScript 执行 XOR 解密
    ↓
浏览器触发文件下载（Blob API）
```

**技术特点：**
- 🔒 **完全离线** - 所有数据在浏览器内存中处理
- ⚡ **高性能** - WASM 加速，处理速度 10+ MB/s
- 📊 **透明可见** - 完整显示解密过程的每个步骤
- 🛡️ **安全隐私** - 数据不经过任何服务器

#### 🔑 密钥流生成模式

为 Python CLI/GUI 工具生成密钥流文件：

1. 生成 131,072 字节的 Isaac64 密钥流
2. 导出为十六进制文本文件
3. 配合 Python 工具离线解密

### 部署到 GitHub Pages

**自己部署：**

1. Fork 本仓库或上传到你的 GitHub
2. 进入仓库设置 **Settings → Pages**
3. **Source** 选择 `main` 分支，目录选择 `/ (root)`
4. 保存后等待几分钟
5. 访问：`https://your-username.github.io/repo-name/`

**使用官方部署：**

直接访问：https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/

### 浏览器兼容性

| 浏览器 | 最低版本 | 说明 |
|--------|---------|------|
| Chrome | 57+ | ✅ 完全支持 |
| Edge | 79+ | ✅ 完全支持 |
| Firefox | 52+ | ✅ 完全支持 |
| Safari | 11+ | ✅ 完全支持 |
| Opera | 44+ | ✅ 完全支持 |

**必需功能：**
- WebAssembly 支持
- File API (FileReader)
- Blob API
- Async/Await

## 🎯 项目信息

- **作者**: Evil0ctal
- **项目**: WeChat Channels Video Decryption Tool
- **GitHub**: https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption
- **在线工具**: https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
- **项目赞助方**: [TikHub.io](https://tikhub.io) - 专业的社交媒体数据 API 服务平台

# 样本备注

1. [微信安装包 v3.9.8.15](https://github.com/tom-snow/wechat-windows-versions/releases/tag/v3.9.8.15)
2. [wasm\_video\_decode.wasm v1.2.46](https://aladin.wxqcloud.qq.com/aladin/ffmepeg/video-decode/1.2.46/wasm_video_decode.wasm)
3. [worker\_release.js v1.2.46](https://aladin.wxqcloud.qq.com/aladin/ffmepeg/video-decode/1.2.46/worker_release.js)
4. [wasm\_video\_decode.js v1.2.46](https://aladin.wxqcloud.qq.com/aladin/ffmepeg/video-decode/1.2.46/wasm_video_decode.js)
5. [wasm\_video\_decode\_fallback.js v1.2.46](https://aladin.wxqcloud.qq.com/aladin/ffmepeg/video-decode/1.2.46/wasm_video_decode_fallback.js)


## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## ⚠️ 免责声明

本工具仅供学习和研究使用。请遵守相关法律法规和平台服务条款。