#!/bin/bash

# ==========================================
# 微信视频解密服务监控脚本 (原生模式)
# WeChat Video Decryption Service Monitor Script (Native)
# ==========================================

# 配置变量
SERVICE_NAME="wechat-decrypt-api"
SERVICE_PORT="8010"
DEPLOY_DIR="/opt/wechat-decrypt-api"
SERVICE_USER="wechat-api"
LOG_DIR="/var/log/wechat-decrypt-api"
ALERT_EMAIL=""  # 设置告警邮箱

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

# 检查systemd服务状态
check_systemd_service() {
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo "✅ systemd服务状态: 运行中"
        return 0
    else
        echo "❌ systemd服务状态: 已停止"
        return 1
    fi
}

# 检查PM2进程状态
check_pm2_process() {
    local pm2_status
    pm2_status=$(sudo -u $SERVICE_USER pm2 jlist 2>/dev/null | jq -r ".[] | select(.name==\"$SERVICE_NAME\") | .pm2_env.status" 2>/dev/null)
    
    if [[ "$pm2_status" == "online" ]]; then
        echo "✅ PM2进程状态: 在线"
        return 0
    elif [[ "$pm2_status" == "stopped" ]]; then
        echo "❌ PM2进程状态: 已停止"
        return 1
    elif [[ "$pm2_status" == "errored" ]]; then
        echo "❌ PM2进程状态: 错误"
        return 1
    else
        echo "❌ PM2进程状态: 未知或不存在"
        return 1
    fi
}

# 检查端口监听
check_port_listening() {
    if netstat -tlnp 2>/dev/null | grep -q ":$SERVICE_PORT "; then
        echo "✅ 端口监听: $SERVICE_PORT 正常"
        return 0
    else
        echo "❌ 端口监听: $SERVICE_PORT 未监听"
        return 1
    fi
}

# 健康检查
check_health_endpoint() {
    local response
    local http_code
    
    response=$(curl -s -w "%{http_code}" http://localhost:$SERVICE_PORT/health 2>/dev/null)
    http_code="${response: -3}"
    
    if [[ "$http_code" == "200" ]]; then
        echo "✅ 健康检查: 通过 (HTTP $http_code)"
        return 0
    else
        echo "❌ 健康检查: 失败 (HTTP $http_code)"
        return 1
    fi
}

# 检查内存使用
check_memory_usage() {
    local pid
    local memory_mb
    
    # 获取PM2进程的PID
    pid=$(sudo -u $SERVICE_USER pm2 jlist 2>/dev/null | jq -r ".[] | select(.name==\"$SERVICE_NAME\") | .pid" 2>/dev/null)
    
    if [[ -n "$pid" && "$pid" != "null" ]]; then
        memory_mb=$(ps -p $pid -o rss= 2>/dev/null | awk '{print int($1/1024)}')
        if [[ -n "$memory_mb" ]]; then
            echo "📊 内存使用: ${memory_mb}MB"
            
            # 内存告警阈值 (2GB)
            if [[ $memory_mb -gt 2048 ]]; then
                log_warn "内存使用过高: ${memory_mb}MB"
                return 1
            fi
        else
            echo "❓ 内存使用: 无法获取"
        fi
    else
        echo "❓ 内存使用: 进程不存在"
        return 1
    fi
    
    return 0
}

# 检查CPU使用
check_cpu_usage() {
    local pid
    local cpu_percent
    
    # 获取PM2进程的PID
    pid=$(sudo -u $SERVICE_USER pm2 jlist 2>/dev/null | jq -r ".[] | select(.name==\"$SERVICE_NAME\") | .pid" 2>/dev/null)
    
    if [[ -n "$pid" && "$pid" != "null" ]]; then
        cpu_percent=$(ps -p $pid -o %cpu= 2>/dev/null | awk '{print int($1)}')
        if [[ -n "$cpu_percent" ]]; then
            echo "📊 CPU使用: ${cpu_percent}%"
            
            # CPU告警阈值 (80%)
            if [[ $cpu_percent -gt 80 ]]; then
                log_warn "CPU使用过高: ${cpu_percent}%"
                return 1
            fi
        else
            echo "❓ CPU使用: 无法获取"
        fi
    else
        echo "❓ CPU使用: 进程不存在"
        return 1
    fi
    
    return 0
}

# 检查磁盘空间
check_disk_space() {
    local disk_usage
    local log_disk_usage
    
    # 检查根分区
    disk_usage=$(df / | awk 'NR==2{print int($5)}' | sed 's/%//')
    echo "📊 根分区使用: ${disk_usage}%"
    
    # 检查日志目录
    if [[ -d "$LOG_DIR" ]]; then
        log_disk_usage=$(du -sh $LOG_DIR 2>/dev/null | awk '{print $1}')
        echo "📊 日志目录大小: $log_disk_usage"
    fi
    
    # 磁盘告警阈值 (85%)
    if [[ $disk_usage -gt 85 ]]; then
        log_warn "磁盘使用过高: ${disk_usage}%"
        return 1
    fi
    
    return 0
}

# 检查日志文件
check_log_files() {
    local error_count
    local recent_errors
    
    if [[ -f "$LOG_DIR/error.log" ]]; then
        # 检查最近5分钟的错误日志
        recent_errors=$(find $LOG_DIR/error.log -mmin -5 -exec wc -l {} \; 2>/dev/null | awk '{print $1}')
        if [[ -n "$recent_errors" && $recent_errors -gt 0 ]]; then
            error_count=$(tail -n 100 $LOG_DIR/error.log | grep -c "ERROR\|Error\|error" 2>/dev/null || echo "0")
            if [[ $error_count -gt 5 ]]; then
                echo "⚠️  最近错误日志: ${error_count}条"
                return 1
            else
                echo "✅ 错误日志: 正常"
            fi
        else
            echo "✅ 错误日志: 正常"
        fi
    else
        echo "❓ 错误日志: 文件不存在"
    fi
    
    return 0
}

# 重启服务
restart_service() {
    log_warn "尝试重启服务..."
    
    # 先尝试重启PM2进程
    sudo -u $SERVICE_USER pm2 restart $SERVICE_NAME
    sleep 10
    
    # 如果PM2重启失败，重启systemd服务
    if ! check_pm2_process > /dev/null; then
        log_warn "PM2重启失败，尝试重启systemd服务..."
        systemctl restart $SERVICE_NAME
        sleep 15
    fi
    
    # 验证重启结果
    if check_health_endpoint > /dev/null; then
        log_info "服务重启成功"
        return 0
    else
        log_error "服务重启失败"
        return 1
    fi
}

# 发送告警邮件
send_alert() {
    local subject="$1"
    local message="$2"
    
    if [[ -n "$ALERT_EMAIL" ]] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "$subject" "$ALERT_EMAIL"
        log_info "告警邮件已发送到: $ALERT_EMAIL"
    fi
}

# 清理日志文件
cleanup_logs() {
    log_step "清理日志文件..."
    
    # 清理超过7天的日志
    find $LOG_DIR -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    # 压缩大于100MB的日志文件
    find $LOG_DIR -name "*.log" -size +100M -exec gzip {} \; 2>/dev/null || true
    
    # 删除超过30天的压缩日志
    find $LOG_DIR -name "*.log.gz" -mtime +30 -delete 2>/dev/null || true
    
    log_info "日志清理完成"
}

# 显示服务状态
show_status() {
    echo "=================================="
    echo "微信视频解密服务状态 (原生模式)"
    echo "=================================="
    echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    # 基础状态检查
    check_systemd_service
    check_pm2_process
    check_port_listening
    check_health_endpoint
    echo ""
    
    # 资源使用检查
    echo "资源使用情况:"
    check_memory_usage
    check_cpu_usage
    check_disk_space
    echo ""
    
    # 日志检查
    echo "日志状态:"
    check_log_files
    echo ""
    
    # PM2详细信息
    echo "PM2进程详情:"
    sudo -u $SERVICE_USER pm2 show $SERVICE_NAME 2>/dev/null || echo "PM2进程信息获取失败"
    echo ""
    
    # 最近的日志
    echo "最近的应用日志 (最后10行):"
    if [[ -f "$LOG_DIR/out.log" ]]; then
        tail -n 10 $LOG_DIR/out.log
    else
        echo "日志文件不存在"
    fi
    
    echo "=================================="
}

# 监控模式 (持续监控)
monitor_mode() {
    log_info "启动监控模式..."
    
    local check_interval=60  # 检查间隔(秒)
    local failure_count=0
    local max_failures=3
    
    while true; do
        local all_checks_passed=true
        
        # 执行所有检查
        if ! check_systemd_service > /dev/null; then
            all_checks_passed=false
        fi
        
        if ! check_pm2_process > /dev/null; then
            all_checks_passed=false
        fi
        
        if ! check_health_endpoint > /dev/null; then
            all_checks_passed=false
        fi
        
        if ! check_memory_usage > /dev/null; then
            all_checks_passed=false
        fi
        
        if ! check_cpu_usage > /dev/null; then
            all_checks_passed=false
        fi
        
        if ! check_disk_space > /dev/null; then
            all_checks_passed=false
        fi
        
        if ! check_log_files > /dev/null; then
            all_checks_passed=false
        fi
        
        # 处理检查结果
        if [[ "$all_checks_passed" == "true" ]]; then
            failure_count=0
            log_info "所有检查通过"
        else
            ((failure_count++))
            log_warn "检查失败 ($failure_count/$max_failures)"
            
            if [[ $failure_count -ge $max_failures ]]; then
                log_error "连续失败次数达到阈值，尝试重启服务"
                
                if restart_service; then
                    failure_count=0
                    send_alert "服务自动重启成功" "微信视频解密服务检测到异常并已自动重启成功"
                else
                    send_alert "服务自动重启失败" "微信视频解密服务检测到异常，自动重启失败，需要人工干预"
                    log_error "自动重启失败，需要人工干预"
                fi
            fi
        fi
        
        sleep $check_interval
    done
}

# 显示帮助信息
show_help() {
    echo "微信视频解密服务监控脚本 (原生模式)"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  status     显示服务状态"
    echo "  monitor    启动持续监控模式"
    echo "  restart    重启服务"
    echo "  cleanup    清理日志文件"
    echo "  help       显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 status          # 显示当前状态"
    echo "  $0 monitor         # 启动监控模式"
    echo "  $0 restart         # 重启服务"
    echo "  $0 cleanup         # 清理日志"
}

# 主函数
main() {
    case "${1:-status}" in
        "status")
            show_status
            ;;
        "monitor")
            monitor_mode
            ;;
        "restart")
            restart_service
            ;;
        "cleanup")
            cleanup_logs
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi