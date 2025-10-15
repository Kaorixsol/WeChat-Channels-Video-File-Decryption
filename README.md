# 微信视频号解密工具 / WeChat Channels Video Decryption Tool

一个完整的微信视频号加密视频解密解决方案，基于逆向工程分析实现。本项目使用微信官方的 WebAssembly (WASM) 模块来生成 Isaac64 PRNG 密钥流，并通过 XOR 运算完成视频解密。

## 📖 项目简介

微信视频号使用 **Isaac64**（Indirection, Shift, Accumulate, Add, and Count）密码学伪随机数生成器对视频文件的前 128 KB 数据进行加密。本项目通过以下方式实现完整的解密流程：

- 🔬 **算法分析**：通过逆向工程分析微信客户端，确认使用 Isaac64 PRNG 算法
- 🧩 **WASM 模块**：直接使用微信官方的 `wasm_video_decode.wasm` 模块，保证 100% 兼容性
- 🔑 **密钥流生成**：基于 API 响应中的 `decode_key` 种子值生成 131,072 字节的密钥流
- 🔄 **关键步骤**：密钥流必须经过 `reverse()` 操作（这是成功解密的关键）
- ⚡ **XOR 解密**：对视频前 128 KB 执行 XOR 运算，还原原始 MP4 数据
- 🎯 **多平台支持**：提供在线网页版、命令行工具、图形界面三种使用方式

**技术栈：** JavaScript (WASM), Python 3.x, tkinter, HTML5

## ✨ 特性

- ✅ 使用微信官方 WASM 模块（保证兼容性）
- ✅ 支持完整视频解密
- ✅ 提供三种使用方式：在线网页版、命令行版、图形界面版
- ✅ 支持交互模式和命令行参数模式
- ✅ 包含示例文件和测试数据

## 🚀 快速开始

### 前置要求

- Python 3.x
- 现代浏览器 (Chrome/Edge/Safari/Firefox)

### 方式一：图形界面（推荐新手）

最简单的使用方式，无需命令行操作：

```bash
python3 decrypt_wechat_video_gui.py
```

在图形界面中：
1. 选择或粘贴密钥流
2. 选择加密视频文件
3. 点击"开始解密"按钮
4. 等待解密完成

![GUI Screenshot](https://via.placeholder.com/600x400?text=GUI+Screenshot)

### 方式二：命令行（推荐进阶用户）

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

### 方式三：在线网页版

#### 步骤 1：生成密钥流

访问在线页面或本地服务器：
```bash
# 本地模式
python3 -m http.server 8888
open http://localhost:8888/index.html

# 或直接访问 GitHub Pages
# https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/
```

在网页中：
1. 输入 `decode_key`（从 API 响应中获取）
2. 点击 "🚀 生成密钥流"
3. 点击 "💾 导出密钥流" 下载文件

#### 步骤 2：解密视频

```bash
# 移动密钥流文件到项目目录
mv ~/Downloads/keystream_131072_bytes.txt .

# 使用 CLI 或 GUI 工具解密
python3 decrypt_wechat_video_cli.py
# 或
python3 decrypt_wechat_video_gui.py
```

## 📁 文件说明

```
WeChat-Channels-Video-File-Decryption/
├── index.html                      # 在线密钥流生成器（GitHub Pages）
├── decrypt_wechat_video_cli.py     # 命令行解密工具（推荐）
├── decrypt_wechat_video_gui.py     # 图形界面解密工具（新手友好）
├── wx_response.json                # API 响应示例（包含 decode_key）
├── wx_encrypted.mp4                # 示例加密文件
├── wx_decrypted.mp4                # 示例解密文件
├── wechat_files/                   # 微信官方 WASM 模块
│   ├── wasm_video_decode.wasm      # Isaac64 WASM 模块
│   ├── wasm_video_decode.js        # WASM 加载器
│   └── ...
├── LICENSE                         # MIT 许可证
└── README.md                       # 本文件
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
        "url": "https://...",
        "file_size": 14088528
      }]
    }
  }
}
```

## 📝 使用示例

### 示例 1: GUI 图形界面（最简单）

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

### 示例 2: CLI 交互模式

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

### 示例 3: CLI 命令行模式（自动化）

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

### 示例 4: 解密已提供的测试文件

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

### 示例 5: 解密新视频（完整流程）

1. **获取视频信息**
   ```bash
   # 抓包获取 API 响应
   # 提取 decode_key 和视频 URL
   ```

2. **下载加密视频**
   ```bash
   curl -o my_encrypted_video.mp4 "视频URL"
   ```

3. **生成密钥流**

   访问在线页面：
   - https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/

   或本地启动：
   ```bash
   python3 -m http.server 8888
   open http://localhost:8888/index.html
   ```

   在页面中：
   - 输入你的 `decode_key`
   - 点击 "生成密钥流"
   - 点击 "导出密钥流" 下载文件

4. **解密视频**
   ```bash
   # GUI 方式
   python3 decrypt_wechat_video_gui.py

   # 或 CLI 方式
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

1. **必须使用 reverse() 操作**
   - 密钥流必须反转才能正确解密
   - HTML 页面已自动处理此步骤

2. **decode_key 必须匹配**
   - 每个视频有唯一的 decode_key
   - 使用错误的 key 会导致解密失败

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

## 🌐 GitHub Pages 在线使用

### 部署到 GitHub Pages

1. Fork 本仓库或上传到你的 GitHub
2. 进入仓库设置 Settings → Pages
3. Source 选择 `main` 分支，目录选择 `/ (root)`
4. 保存后等待几分钟，访问：`https://your-username.github.io/repo-name/`

### 使用在线版本

如果项目已部署到 GitHub Pages，可以直接在线使用：

1. 访问在线页面（例如：`https://evil0ctal.github.io/WeChat-Channels-Video-File-Decryption/`）
2. 输入 `decode_key` 并点击 "🚀 Test Decryption"
3. 点击 "💾 Export Keystream" 导出密钥流
4. 下载密钥流文件后，本地运行 `decrypt_full_video.py` 解密

**优势**：无需本地启动 HTTP 服务器，直接在线生成密钥流！

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## ⚠️ 免责声明

本工具仅供学习和研究使用。请遵守相关法律法规和平台服务条款。

---

**最后更新**: 2025-10-15
**状态**: ✅ 测试通过
