#!/bin/bash

# ==========================================
# 微信视频解密服务原生部署脚本 (无Docker)
# WeChat Video Decryption Service Native Deploy Script
# ==========================================

set -e  # 遇到错误立即退出

# 配置变量
SERVICE_NAME="wechat-decrypt-api"
SERVICE_PORT="8010"
DEPLOY_DIR="/opt/wechat-decrypt-api"
SERVICE_USER="wechat-api"
LOG_DIR="/var/log/wechat-decrypt-api"
NODE_VERSION="18"  # Node.js版本

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        exit 1
    fi
}

# 检查系统要求
check_system() {
    log_step "检查系统要求..."
    
    # 检查操作系统
    if [[ ! -f /etc/os-release ]]; then
        log_error "无法检测操作系统版本"
        exit 1
    fi
    
    # 检查内存
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $MEMORY_GB -lt 2 ]]; then
        log_warn "系统内存少于2GB，可能影响服务性能"
    fi
    
    # 检查磁盘空间
    DISK_SPACE=$(df / | awk 'NR==2{print $4}')
    if [[ $DISK_SPACE -lt 3000000 ]]; then  # 3GB
        log_warn "根分区可用空间少于3GB"
    fi
    
    log_info "系统检查完成"
}

# 安装系统依赖
install_system_dependencies() {
    log_step "安装系统依赖..."
    
    # 更新包管理器
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y curl wget git unzip software-properties-common build-essential
        
        # 安装Chromium浏览器依赖
        apt-get install -y \
            libnss3 \
            libnspr4 \
            libatk1.0-0 \
            libatk-bridge2.0-0 \
            libcups2 \
            libdrm2 \
            libdbus-1-3 \
            libxkbcommon0 \
            libxcomposite1 \
            libxdamage1 \
            libxfixes3 \
            libxrandr2 \
            libgbm1 \
            libpango-1.0-0 \
            libcairo2 \
            libasound2 \
            libatspi2.0-0 \
            fonts-liberation \
            libappindicator3-1 \
            libgtk-3-0 \
            libxss1 \
            xdg-utils
            
    elif command -v yum &> /dev/null; then
        yum update -y
        yum groupinstall -y "Development Tools"
        yum install -y curl wget git unzip
        
        # 安装Chromium依赖 (CentOS/RHEL)
        yum install -y \
            nss \
            nspr \
            atk \
            at-spi2-atk \
            cups-libs \
            libdrm \
            dbus-libs \
            libxkbcommon \
            libXcomposite \
            libXdamage \
            libXfixes \
            libXrandr \
            mesa-libgbm \
            pango \
            cairo \
            alsa-lib \
            at-spi2-core \
            liberation-fonts \
            gtk3 \
            libXScrnSaver
            
    else
        log_error "不支持的包管理器"
        exit 1
    fi
    
    log_info "系统依赖安装完成"
}

# 安装Node.js
install_nodejs() {
    log_step "安装Node.js..."
    
    # 检查是否已安装Node.js
    if command -v node &> /dev/null; then
        CURRENT_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [[ $CURRENT_VERSION -ge $NODE_VERSION ]]; then
            log_info "Node.js已安装，版本: $(node --version)"
            return
        fi
    fi
    
    # 安装Node.js
    log_info "安装Node.js $NODE_VERSION..."
    
    # 使用NodeSource仓库安装
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash -
    
    if command -v apt-get &> /dev/null; then
        apt-get install -y nodejs
    elif command -v yum &> /dev/null; then
        yum install -y nodejs npm
    fi
    
    # 验证安装
    if command -v node &> /dev/null && command -v npm &> /dev/null; then
        log_info "Node.js安装成功，版本: $(node --version)"
        log_info "npm版本: $(npm --version)"
    else
        log_error "Node.js安装失败"
        exit 1
    fi
}

# 安装PM2进程管理器
install_pm2() {
    log_step "安装PM2进程管理器..."
    
    if command -v pm2 &> /dev/null; then
        log_info "PM2已安装，版本: $(pm2 --version)"
        return
    fi
    
    npm install -g pm2
    
    # 设置PM2开机自启动
    pm2 startup
    
    log_info "PM2安装完成"
}

# 创建服务用户
create_service_user() {
    log_step "创建服务用户..."
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/bash -d $DEPLOY_DIR $SERVICE_USER
        log_info "创建用户: $SERVICE_USER"
    else
        log_info "用户已存在: $SERVICE_USER"
    fi
}

# 创建目录结构
create_directories() {
    log_step "创建目录结构..."
    
    mkdir -p $DEPLOY_DIR
    mkdir -p $LOG_DIR
    mkdir -p /etc/systemd/system
    
    # 设置权限
    chown -R $SERVICE_USER:$SERVICE_USER $DEPLOY_DIR
    chown -R $SERVICE_USER:$SERVICE_USER $LOG_DIR
    
    log_info "目录结构创建完成"
}

# 部署应用代码
deploy_application() {
    log_step "部署应用代码..."
    
    # 如果是从Git仓库部署
    if [[ -n "${GIT_REPO:-}" ]]; then
        log_info "从Git仓库克隆代码: $GIT_REPO"
        rm -rf $DEPLOY_DIR/app
        git clone $GIT_REPO $DEPLOY_DIR/temp
        mv $DEPLOY_DIR/temp/api-service $DEPLOY_DIR/app
        rm -rf $DEPLOY_DIR/temp
    else
        # 如果是本地部署，复制当前目录
        log_info "复制本地代码到部署目录"
        rm -rf $DEPLOY_DIR/app
        cp -r . $DEPLOY_DIR/app/
    fi
    
    cd $DEPLOY_DIR/app
    
    # 设置权限
    chown -R $SERVICE_USER:$SERVICE_USER $DEPLOY_DIR/app
    
    log_info "应用代码部署完成"
}

# 安装应用依赖
install_app_dependencies() {
    log_step "安装应用依赖..."
    
    cd $DEPLOY_DIR/app
    
    # 切换到服务用户执行npm install
    sudo -u $SERVICE_USER npm install --production
    
    # 安装Playwright浏览器
    log_info "安装Playwright Chromium浏览器..."
    sudo -u $SERVICE_USER npx playwright install chromium --with-deps
    
    log_info "应用依赖安装完成"
}

# 创建PM2配置文件
create_pm2_config() {
    log_step "创建PM2配置文件..."
    
    cat > $DEPLOY_DIR/app/ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: '$SERVICE_NAME',
    script: 'server.js',
    cwd: '$DEPLOY_DIR/app',
    user: '$SERVICE_USER',
    instances: 1,
    exec_mode: 'fork',
    
    // 环境变量
    env: {
      NODE_ENV: 'production',
      PORT: $SERVICE_PORT
    },
    
    // 日志配置
    log_file: '$LOG_DIR/app.log',
    out_file: '$LOG_DIR/out.log',
    error_file: '$LOG_DIR/error.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    
    // 重启策略
    autorestart: true,
    max_restarts: 10,
    min_uptime: '10s',
    max_memory_restart: '2G',
    
    // 监控
    watch: false,
    ignore_watch: ['node_modules', 'logs'],
    
    // 其他配置
    kill_timeout: 5000,
    wait_ready: true,
    listen_timeout: 10000
  }]
};
EOF
    
    chown $SERVICE_USER:$SERVICE_USER $DEPLOY_DIR/app/ecosystem.config.js
    log_info "PM2配置文件创建完成"
}

# 创建systemd服务文件
create_systemd_service() {
    log_step "创建systemd服务..."
    
    cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=WeChat Video Decryption API Service (Native)
After=network.target
StartLimitIntervalSec=60
StartLimitBurst=3

[Service]
Type=forking
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$DEPLOY_DIR/app

# 环境变量
Environment=NODE_ENV=production
Environment=PORT=$SERVICE_PORT
Environment=HOME=$DEPLOY_DIR

# PM2命令
ExecStart=/usr/bin/pm2 start ecosystem.config.js --no-daemon
ExecReload=/usr/bin/pm2 reload ecosystem.config.js
ExecStop=/usr/bin/pm2 stop ecosystem.config.js

# 重启策略
Restart=on-failure
RestartSec=10

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$DEPLOY_DIR $LOG_DIR

# 超时设置
TimeoutStartSec=60
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载systemd
    systemctl daemon-reload
    systemctl enable $SERVICE_NAME
    
    log_info "systemd服务创建完成"
}

# 配置防火墙
configure_firewall() {
    log_step "配置防火墙..."
    
    if command -v ufw &> /dev/null; then
        ufw allow $SERVICE_PORT/tcp
        log_info "UFW防火墙规则已添加"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=$SERVICE_PORT/tcp
        firewall-cmd --reload
        log_info "firewalld防火墙规则已添加"
    else
        log_warn "未检测到防火墙，请手动开放端口 $SERVICE_PORT"
    fi
}

# 启动服务
start_service() {
    log_step "启动服务..."
    
    # 首先以服务用户身份启动PM2
    sudo -u $SERVICE_USER bash -c "cd $DEPLOY_DIR/app && pm2 start ecosystem.config.js"
    
    # 保存PM2进程列表
    sudo -u $SERVICE_USER pm2 save
    
    # 启动systemd服务
    systemctl start $SERVICE_NAME
    
    # 等待服务启动
    sleep 15
    
    # 检查服务状态
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_info "服务启动成功"
    else
        log_error "服务启动失败"
        systemctl status $SERVICE_NAME
        sudo -u $SERVICE_USER pm2 logs $SERVICE_NAME --lines 20
        exit 1
    fi
}

# 健康检查
health_check() {
    log_step "执行健康检查..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s http://localhost:$SERVICE_PORT/health > /dev/null; then
            log_info "健康检查通过"
            return 0
        fi
        
        log_info "等待服务启动... ($attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done
    
    log_error "健康检查失败"
    return 1
}

# 显示部署信息
show_deployment_info() {
    log_step "部署信息"
    
    echo "=================================="
    echo "微信视频解密服务部署完成 (原生模式)"
    echo "=================================="
    echo "服务名称: $SERVICE_NAME"
    echo "服务端口: $SERVICE_PORT"
    echo "部署目录: $DEPLOY_DIR"
    echo "日志目录: $LOG_DIR"
    echo "服务用户: $SERVICE_USER"
    echo "Node.js版本: $(node --version)"
    echo "PM2版本: $(pm2 --version)"
    echo ""
    echo "API端点:"
    echo "  健康检查: http://localhost:$SERVICE_PORT/health"
    echo "  服务信息: http://localhost:$SERVICE_PORT/api/info"
    echo "  解密接口: http://localhost:$SERVICE_PORT/api/decrypt"
    echo ""
    echo "管理命令:"
    echo "  启动服务: systemctl start $SERVICE_NAME"
    echo "  停止服务: systemctl stop $SERVICE_NAME"
    echo "  重启服务: systemctl restart $SERVICE_NAME"
    echo "  查看状态: systemctl status $SERVICE_NAME"
    echo ""
    echo "PM2管理命令:"
    echo "  查看进程: sudo -u $SERVICE_USER pm2 list"
    echo "  查看日志: sudo -u $SERVICE_USER pm2 logs $SERVICE_NAME"
    echo "  重启应用: sudo -u $SERVICE_USER pm2 restart $SERVICE_NAME"
    echo "  停止应用: sudo -u $SERVICE_USER pm2 stop $SERVICE_NAME"
    echo ""
    echo "日志文件:"
    echo "  应用日志: $LOG_DIR/app.log"
    echo "  输出日志: $LOG_DIR/out.log"
    echo "  错误日志: $LOG_DIR/error.log"
    echo "=================================="
}

# 主函数
main() {
    log_info "开始部署微信视频解密服务 (原生模式)..."
    
    check_root
    check_system
    install_system_dependencies
    install_nodejs
    install_pm2
    create_service_user
    create_directories
    deploy_application
    install_app_dependencies
    create_pm2_config
    create_systemd_service
    configure_firewall
    start_service
    
    if health_check; then
        show_deployment_info
        log_info "部署成功完成！"
    else
        log_error "部署失败，请检查日志"
        echo ""
        echo "故障排除命令:"
        echo "  查看PM2日志: sudo -u $SERVICE_USER pm2 logs $SERVICE_NAME"
        echo "  查看systemd日志: journalctl -u $SERVICE_NAME -f"
        echo "  查看应用日志: tail -f $LOG_DIR/error.log"
        exit 1
    fi
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi