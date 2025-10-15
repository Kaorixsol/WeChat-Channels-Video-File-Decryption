#!/usr/bin/env python3
"""
微信视频号解密工具 - 图形界面版本
使用 tkinter 提供友好的图形界面

Author: Evil0ctal
GitHub: https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path

# 导入 CLI 模块的函数
from decrypt_wechat_video_cli import (
    read_keystream_from_file,
    read_keystream_from_string,
    decrypt_video
)


class DecryptionGUI:
    """解密工具 GUI 主类"""

    def __init__(self, root):
        self.root = root
        self.root.title("微信视频号解密工具")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # 设置应用图标（如果有的话）
        try:
            # 可以添加图标
            pass
        except:
            pass

        # 变量
        self.keystream_file_var = tk.StringVar(value="keystream_131072_bytes.txt")
        self.encrypted_file_var = tk.StringVar(value="wx_encrypted.mp4")
        self.output_file_var = tk.StringVar(value="wx_decrypted.mp4")
        self.keystream_data = None
        self.is_decrypting = False

        # 创建 UI
        self.create_widgets()

        # 检查默认密钥流文件
        self.check_default_keystream()

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="🎬 微信视频号解密工具",
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 第一部分：密钥流
        row = 1
        ttk.Label(main_frame, text="密钥流文件:", font=("Arial", 11)).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.keystream_file_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5
        )
        ttk.Button(main_frame, text="选择文件", command=self.browse_keystream).grid(
            row=row, column=2, pady=5
        )

        # 密钥流状态
        row += 1
        self.keystream_status_label = ttk.Label(
            main_frame,
            text="等待加载密钥流...",
            foreground="gray"
        )
        self.keystream_status_label.grid(
            row=row, column=1, sticky=tk.W, pady=(0, 10)
        )

        # 或者直接输入密钥流
        row += 1
        ttk.Label(main_frame, text="或粘贴密钥流:", font=("Arial", 11)).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.hex_input = scrolledtext.ScrolledText(
            main_frame,
            height=3,
            width=50,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.hex_input.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)

        row += 1
        ttk.Button(
            main_frame,
            text="从文本加载密钥流",
            command=self.load_keystream_from_text
        ).grid(row=row, column=1, sticky=tk.W, pady=(0, 15))

        # 分隔线
        row += 1
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10
        )

        # 第二部分：加密文件
        row += 1
        ttk.Label(main_frame, text="加密视频文件:", font=("Arial", 11)).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.encrypted_file_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5
        )
        ttk.Button(main_frame, text="选择文件", command=self.browse_encrypted).grid(
            row=row, column=2, pady=5
        )

        # 第三部分：输出文件
        row += 1
        ttk.Label(main_frame, text="输出文件名:", font=("Arial", 11)).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.output_file_var, width=50).grid(
            row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5
        )
        ttk.Button(main_frame, text="另存为", command=self.browse_output).grid(
            row=row, column=2, pady=5
        )

        # 分隔线
        row += 1
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10
        )

        # 解密按钮
        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)

        self.decrypt_button = ttk.Button(
            button_frame,
            text="🚀 开始解密",
            command=self.start_decryption,
            width=20
        )
        self.decrypt_button.grid(row=0, column=0, padx=5)

        self.open_folder_button = ttk.Button(
            button_frame,
            text="📂 打开文件夹",
            command=self.open_output_folder,
            state=tk.DISABLED,
            width=20
        )
        self.open_folder_button.grid(row=0, column=1, padx=5)

        ttk.Button(
            button_frame,
            text="❓ 帮助",
            command=self.show_help,
            width=15
        ).grid(row=0, column=2, padx=5)

        # 日志输出区域
        row += 1
        ttk.Label(main_frame, text="操作日志:", font=("Arial", 11)).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5)
        )

        row += 1
        self.log_text = scrolledtext.ScrolledText(
            main_frame,
            height=15,
            width=80,
            wrap=tk.WORD,
            font=("Courier", 9),
            state=tk.DISABLED
        )
        self.log_text.grid(
            row=row, column=0, columnspan=3,
            sticky=(tk.W, tk.E, tk.N, tk.S),
            pady=5
        )

        # 配置日志文本标签
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("info", foreground="blue")

        # 状态栏
        row += 1
        self.status_label = ttk.Label(
            main_frame,
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.grid(
            row=row, column=0, columnspan=3,
            sticky=(tk.W, tk.E), pady=(10, 0)
        )

        # 配置行列权重使文本框可扩展
        main_frame.rowconfigure(row - 1, weight=1)

        # 欢迎信息
        self.log("欢迎使用微信视频号解密工具！", "info")
        self.log("作者: Evil0ctal", "info")
        self.log("项目地址: https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption\n", "info")

    def log(self, message, tag=None):
        """添加日志"""
        self.log_text.config(state=tk.NORMAL)
        if tag:
            self.log_text.insert(tk.END, message + "\n", tag)
        else:
            self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def check_default_keystream(self):
        """检查默认密钥流文件"""
        keystream_file = self.keystream_file_var.get()
        if os.path.exists(keystream_file):
            self.keystream_data = read_keystream_from_file(keystream_file, verbose=False)
            if self.keystream_data:
                size_kb = len(self.keystream_data) / 1024
                self.keystream_status_label.config(
                    text=f"✅ 已加载密钥流 ({size_kb:.2f} KB)",
                    foreground="green"
                )
                self.log(f"✅ 自动加载密钥流文件: {keystream_file}", "success")
            else:
                self.keystream_status_label.config(
                    text="❌ 密钥流文件格式错误",
                    foreground="red"
                )
        else:
            self.keystream_status_label.config(
                text="⚠️ 未找到默认密钥流文件",
                foreground="orange"
            )

    def browse_keystream(self):
        """选择密钥流文件"""
        filename = filedialog.askopenfilename(
            title="选择密钥流文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            self.keystream_file_var.set(filename)
            self.keystream_data = read_keystream_from_file(filename, verbose=False)
            if self.keystream_data:
                size_kb = len(self.keystream_data) / 1024
                self.keystream_status_label.config(
                    text=f"✅ 已加载密钥流 ({size_kb:.2f} KB)",
                    foreground="green"
                )
                self.log(f"✅ 加载密钥流文件: {filename}", "success")
            else:
                self.keystream_status_label.config(
                    text="❌ 密钥流文件格式错误",
                    foreground="red"
                )
                self.log(f"❌ 加载密钥流失败: {filename}", "error")

    def load_keystream_from_text(self):
        """从文本框加载密钥流"""
        hex_string = self.hex_input.get("1.0", tk.END).strip()
        if not hex_string:
            messagebox.showwarning("警告", "请粘贴十六进制密钥流！")
            return

        self.keystream_data = read_keystream_from_string(hex_string, verbose=False)
        if self.keystream_data:
            size_kb = len(self.keystream_data) / 1024
            self.keystream_status_label.config(
                text=f"✅ 已加载密钥流 ({size_kb:.2f} KB)",
                foreground="green"
            )
            self.log(f"✅ 从文本加载密钥流成功 ({size_kb:.2f} KB)", "success")

            # 保存到文件
            save_file = "keystream_131072_bytes.txt"
            with open(save_file, 'w') as f:
                f.write(hex_string)
            self.log(f"✅ 密钥流已保存到: {save_file}", "info")
        else:
            self.keystream_status_label.config(
                text="❌ 密钥流格式错误",
                foreground="red"
            )
            self.log("❌ 密钥流格式错误，请检查输入", "error")

    def browse_encrypted(self):
        """选择加密文件"""
        filename = filedialog.askopenfilename(
            title="选择加密视频文件",
            filetypes=[("MP4 视频", "*.mp4"), ("所有文件", "*.*")]
        )
        if filename:
            self.encrypted_file_var.set(filename)
            self.log(f"✅ 选择加密文件: {filename}", "info")

    def browse_output(self):
        """选择输出文件"""
        filename = filedialog.asksaveasfilename(
            title="保存解密视频",
            defaultextension=".mp4",
            filetypes=[("MP4 视频", "*.mp4"), ("所有文件", "*.*")]
        )
        if filename:
            self.output_file_var.set(filename)
            self.log(f"✅ 输出文件: {filename}", "info")

    def start_decryption(self):
        """开始解密（在线程中执行）"""
        if self.is_decrypting:
            messagebox.showwarning("警告", "正在解密中，请等待...")
            return

        # 验证输入
        if not self.keystream_data:
            messagebox.showerror("错误", "请先加载密钥流文件或粘贴密钥流！")
            return

        encrypted_file = self.encrypted_file_var.get()
        if not os.path.exists(encrypted_file):
            messagebox.showerror("错误", f"加密文件不存在:\n{encrypted_file}")
            return

        output_file = self.output_file_var.get()
        if not output_file:
            messagebox.showerror("错误", "请指定输出文件名！")
            return

        # 禁用按钮
        self.decrypt_button.config(state=tk.DISABLED)
        self.is_decrypting = True

        # 在新线程中执行解密
        thread = threading.Thread(target=self.decrypt_worker, args=(encrypted_file, output_file))
        thread.daemon = True
        thread.start()

    def decrypt_worker(self, encrypted_file, output_file):
        """解密工作线程"""
        try:
            self.log("\n" + "=" * 70, "info")
            self.log("🚀 开始解密...", "info")
            self.log("=" * 70 + "\n", "info")
            self.update_status("正在解密...")

            # 验证密钥流大小
            keystream_size = len(self.keystream_data)
            self.log(f"📊 密钥流大小: {keystream_size:,} bytes ({keystream_size / 1024:.2f} KB)", "info")

            if keystream_size != 131072:
                self.log(f"⚠️  警告: 密钥流大小不是标准的 131072 bytes", "warning")

            # 文件信息
            file_size = os.path.getsize(encrypted_file)
            self.log(f"📁 加密文件: {encrypted_file}", "info")
            self.log(f"📊 文件大小: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)", "info")
            self.log(f"💾 输出文件: {output_file}\n", "info")

            # 调用 CLI 模块的解密函数
            self.log("🔓 开始 XOR 解密...", "info")
            success = decrypt_video(
                encrypted_file,
                self.keystream_data,
                output_file,
                verbose=False  # 我们自己处理日志输出
            )

            # 验证结果
            if success:
                self.log("\n" + "=" * 70, "success")
                self.log("🎉 解密成功！", "success")
                self.log("=" * 70 + "\n", "success")

                output_size = os.path.getsize(output_file)
                self.log(f"✅ 解密文件: {output_file}", "success")
                self.log(f"📊 文件大小: {output_size:,} bytes ({output_size / 1024 / 1024:.2f} MB)", "success")
                self.log(f"📍 完整路径: {os.path.abspath(output_file)}\n", "info")

                self.update_status("解密完成！")

                # 启用打开文件夹按钮
                self.open_folder_button.config(state=tk.NORMAL)

                # 显示成功对话框
                result = messagebox.askyesno(
                    "解密成功",
                    f"视频解密完成！\n\n文件: {output_file}\n\n是否打开文件所在文件夹？"
                )
                if result:
                    self.open_output_folder()
            else:
                self.log("\n" + "=" * 70, "warning")
                self.log("⚠️  解密完成，但可能存在问题", "warning")
                self.log("=" * 70 + "\n", "warning")
                self.log("请检查：", "warning")
                self.log("1. 密钥流是否正确", "warning")
                self.log("2. decode_key 是否匹配此视频", "warning")
                self.log("3. 加密文件是否完整\n", "warning")

                self.update_status("解密完成（可能有问题）")

                messagebox.showwarning(
                    "警告",
                    "解密完成，但未检测到有效的 MP4 签名。\n请检查密钥流和文件是否正确。"
                )

        except Exception as e:
            self.log(f"\n❌ 解密失败: {e}", "error")
            self.update_status("解密失败")
            messagebox.showerror("错误", f"解密失败:\n{e}")
        finally:
            # 恢复按钮
            self.decrypt_button.config(state=tk.NORMAL)
            self.is_decrypting = False

    def open_output_folder(self):
        """打开输出文件所在文件夹"""
        output_file = self.output_file_var.get()
        if os.path.exists(output_file):
            folder = os.path.dirname(os.path.abspath(output_file))
            if sys.platform == "darwin":  # macOS
                os.system(f'open "{folder}"')
            elif sys.platform == "win32":  # Windows
                os.system(f'explorer "{folder}"')
            else:  # Linux
                os.system(f'xdg-open "{folder}"')
        else:
            messagebox.showwarning("警告", "输出文件不存在！")

    def show_help(self):
        """显示帮助信息"""
        help_text = """
微信视频号解密工具 - 使用说明

📝 使用步骤：

1️⃣ 获取密钥流
   方式一：使用浏览器生成
   - 访问项目 GitHub Pages 或启动本地服务器
   - 在页面中输入 decode_key
   - 点击"生成密钥流"
   - 点击"导出密钥流"下载文件

   方式二：直接粘贴
   - 将密钥流十六进制字符串粘贴到文本框
   - 点击"从文本加载密钥流"

2️⃣ 选择加密文件
   - 点击"选择文件"选择加密的 MP4 视频

3️⃣ 指定输出文件
   - 输入输出文件名（默认：wx_decrypted.mp4）

4️⃣ 开始解密
   - 点击"开始解密"按钮
   - 等待解密完成

🔧 技术原理：
- 加密算法：Isaac64 PRNG
- 加密范围：视频前 128 KB
- 解密方式：XOR 运算
- 关键步骤：密钥流必须 reverse()

📌 注意事项：
- 每个视频有唯一的 decode_key
- 密钥流大小应为 131,072 bytes (128 KB)
- 解密后文件头应包含 'ftyp' 签名

🔗 项目地址：
https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption

👨‍💻 作者：Evil0ctal
        """
        messagebox.showinfo("使用帮助", help_text)


def main():
    """主函数"""
    root = tk.Tk()
    app = DecryptionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
