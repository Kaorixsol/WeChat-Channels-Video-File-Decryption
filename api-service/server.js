/**
 * WeChat Channels Video Decryption API Service
 *
 * 基于 Playwright 浏览器自动化的 RPC 解密服务
 * 通过真实浏览器环境完美兼容微信官方 WASM 模块
 *
 * @author Evil0ctal
 * @license MIT
 */

const express = require('express');
const { chromium } = require('playwright');
const multer = require('multer');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8010;

// 配置文件上传
const upload = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: 500 * 1024 * 1024 } // 500MB
});

// 中间件
app.use(cors());
app.use(express.json({ limit: '100mb' }));

// 静态文件服务 - 提供 wechat_files 目录
app.use('/wechat_files', express.static(path.join(__dirname, 'wechat_files')));

// 全局变量
let browser = null;
let page = null;
let server = null;
const getWorkerUrl = () => `http://localhost:${PORT}/worker.html`;

/**
 * 初始化 Playwright 浏览器
 */
async function initBrowser() {
    if (browser && page) {
        return;
    }

    console.log('🚀 启动 Playwright 浏览器...');

    browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    page = await browser.newPage();

    // 加载 RPC Worker 页面（通过 HTTP 以支持本地 WASM 文件加载）
    await page.goto(getWorkerUrl());

    // 等待 WASM 模块完全加载 (等待 Module.WxIsaac64 可用)
    console.log('⏳ 等待 WASM 模块加载...');
    await page.waitForFunction(
        () => typeof Module !== 'undefined' && typeof Module.WxIsaac64 !== 'undefined',
        { timeout: 60000 }
    );

    const status = await page.evaluate(() => window.checkWasmStatus());
    console.log(`   WASM 模块状态: ${JSON.stringify(status)}`);

    // 检查是否使用 CDN
    const usingCdn = await page.evaluate(() => window.WASM_USING_CDN);
    console.log('✅ Playwright 浏览器已就绪');
    console.log(`   Worker URL: ${getWorkerUrl()}`);
    console.log(`   WASM Source: ${usingCdn ? 'WeChat CDN (fallback)' : 'Local files'}`);
    console.log(`   WASM Status: ${status.loaded ? 'Loaded' : 'Not Loaded'}`);
}

/**
 * 请求日志中间件
 */
app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
    next();
});

// ==================== API 路由 ====================

/**
 * GET /health
 * 健康检查
 */
app.get('/health', async (req, res) => {
    try {
        if (!page) {
            await initBrowser();
        }

        const wasmStatus = await page.evaluate(() => window.checkWasmStatus());

        res.json({
            status: 'ok',
            service: 'wechat-decrypt-api',
            version: '2.0.0',
            engine: 'playwright',
            wasm: wasmStatus,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            status: 'error',
            error: error.message
        });
    }
});

/**
 * GET /
 * API 文档页面
 */
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'docs.html'));
});

/**
 * GET /worker.html
 * RPC Worker 页面（供 Playwright 浏览器加载）
 */
app.get('/worker.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'worker.html'));
});

/**
 * GET /api/info
 * 服务信息（JSON 格式）
 */
app.get('/api/info', (req, res) => {
    res.json({
        service: 'WeChat Channels Video Decryption API',
        version: '2.0.0',
        engine: 'Playwright + Chromium',
        author: 'Evil0ctal',
        github: 'https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption',
        endpoints: {
            health: 'GET /health',
            decrypt: 'POST /api/decrypt',
            keystream: 'POST /api/keystream'
        }
    });
});

/**
 * POST /api/keystream
 * 生成密钥流
 */
app.post('/api/keystream', async (req, res) => {
    try {
        const { decode_key, format = 'hex' } = req.body;

        if (!decode_key) {
            return res.status(400).json({ error: '缺少 decode_key 参数' });
        }

        if (!['hex', 'base64'].includes(format)) {
            return res.status(400).json({
                error: '无效的 format 参数',
                valid_formats: ['hex', 'base64']
            });
        }

        // 确保浏览器已初始化
        if (!page) {
            await initBrowser();
        }

        console.log(`🔑 生成密钥流: decode_key=${decode_key}, format=${format}`);

        // 调用浏览器中的 RPC 方法
        const startTime = Date.now();
        const keystreamBase64 = await page.evaluate(async (key) => {
            return await window.generateKeystream(key);
        }, decode_key);

        const duration = Date.now() - startTime;

        // 格式转换
        let keystream;
        if (format === 'hex') {
            const binary = atob(keystreamBase64);
            keystream = Array.from(binary, c =>
                c.charCodeAt(0).toString(16).padStart(2, '0')
            ).join('');
        } else {
            keystream = keystreamBase64;
        }

        console.log(`✅ 密钥流生成成功，耗时 ${duration}ms`);

        res.json({
            decode_key,
            keystream,
            format,
            size: 131072,
            duration_ms: duration,
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        console.error('❌ 密钥流生成失败:', error.message);
        res.status(500).json({ error: error.message });
    }
});

/**
 * POST /api/decrypt
 * 完整解密视频
 */
app.post('/api/decrypt', upload.single('video'), async (req, res) => {
    try {
        const { decode_key } = req.body;
        const videoFile = req.file;

        if (!decode_key) {
            return res.status(400).json({ error: '缺少 decode_key 参数' });
        }

        if (!videoFile) {
            return res.status(400).json({ error: '缺少视频文件' });
        }

        // 确保浏览器已初始化
        if (!page) {
            await initBrowser();
        }

        console.log(`📹 解密请求:`);
        console.log(`   decode_key: ${decode_key}`);
        console.log(`   文件: ${videoFile.originalname} (${(videoFile.size / 1024 / 1024).toFixed(2)} MB)`);

        const startTime = Date.now();

        // 步骤 1: 生成密钥流
        console.log('   [1/3] 生成密钥流...');
        const keystreamBase64 = await page.evaluate(async (key) => {
            return await window.generateKeystream(key);
        }, decode_key);

        // 步骤 2: 转换视频为 Base64
        console.log('   [2/3] 编码视频数据...');
        const encryptedBase64 = videoFile.buffer.toString('base64');

        // 步骤 3: 在浏览器中执行解密
        console.log('   [3/3] 执行 XOR 解密...');
        const decryptedBase64 = await page.evaluate(
            (params) => {
                return window.decryptVideo(params.encrypted, params.keystream);
            },
            { encrypted: encryptedBase64, keystream: keystreamBase64 }
        );

        // Base64 → Buffer
        const decrypted = Buffer.from(decryptedBase64, 'base64');

        // 验证 MP4 签名
        const ftyp = decrypted.toString('utf8', 4, 8);
        if (ftyp !== 'ftyp') {
            throw new Error('解密失败：未找到 MP4 ftyp 签名，请检查 decode_key');
        }

        const duration = Date.now() - startTime;
        console.log(`✅ 解密成功，耗时 ${duration}ms`);

        // 返回解密后的视频
        res.set({
            'Content-Type': 'video/mp4',
            'Content-Length': decrypted.length,
            'Content-Disposition': `attachment; filename="decrypted_${Date.now()}.mp4"`,
            'X-Decrypt-Duration': duration
        });

        res.send(decrypted);

    } catch (error) {
        console.error('❌ 解密失败:', error.message);
        res.status(500).json({ error: error.message });
    }
});

/**
 * 404 处理
 */
app.use((req, res) => {
    res.status(404).json({
        error: '接口不存在',
        path: req.path,
        available: [
            'GET /',
            'GET /health',
            'POST /api/keystream',
            'POST /api/decrypt'
        ]
    });
});

/**
 * 错误处理
 */
app.use((err, req, res, next) => {
    console.error('服务器错误:', err);

    if (err instanceof multer.MulterError) {
        if (err.code === 'LIMIT_FILE_SIZE') {
            return res.status(413).json({
                error: '文件过大',
                limit: '500MB'
            });
        }
    }

    res.status(500).json({ error: err.message });
});

// ==================== 启动服务 ====================

(async () => {
    try {
        console.log('╔═══════════════════════════════════════════════════════════╗');
        console.log('║   WeChat Channels Video Decryption API (Playwright)      ║');
        console.log('╚═══════════════════════════════════════════════════════════╝\n');

        // 先启动 HTTP 服务器（浏览器需要从这里加载 worker.html）
        server = app.listen(PORT, async () => {
            console.log('✅ HTTP 服务器已启动');
            console.log(`📡 监听端口: ${PORT}`);
            console.log(`🌐 访问地址: http://localhost:${PORT}\n`);

            try {
                // 初始化浏览器
                await initBrowser();

                console.log('\n✅ 服务完全就绪');
                console.log('\n📚 API 端点:');
                console.log('   GET  /          服务信息');
                console.log('   GET  /health    健康检查');
                console.log('   POST /api/keystream  生成密钥流');
                console.log('   POST /api/decrypt    解密视频');
                console.log('\n🎭 使用 Playwright 浏览器执行 WASM');
                console.log('   100% 兼容微信官方模块\n');
            } catch (error) {
                console.error('❌ 浏览器初始化失败:', error);
                process.exit(1);
            }
        });

    } catch (error) {
        console.error('❌ 启动失败:', error);
        process.exit(1);
    }
})();

// 优雅关闭
process.on('SIGTERM', async () => {
    console.log('\n👋 正在关闭服务...');
    if (browser) {
        await browser.close();
    }
    process.exit(0);
});

process.on('SIGINT', async () => {
    console.log('\n👋 正在关闭服务...');
    if (browser) {
        await browser.close();
    }
    process.exit(0);
});
