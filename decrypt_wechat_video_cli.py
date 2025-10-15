#!/usr/bin/env python3
"""
微信视频号解密工具 - 命令行版本
使用从浏览器导出的密钥流文件解密视频

Author: Evil0ctal
GitHub: https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption
"""
import sys
import os
import argparse
from pathlib import Path


def read_keystream_from_file(filename, verbose=True):
    """
    从导出的文件读取密钥流

    Args:
        filename: 密钥流文件路径
        verbose: 是否显示详细信息

    Returns:
        bytes: 密钥流数据，失败返回 None
    """
    if verbose:
        print(f"📂 读取密钥流文件: {filename}")

    if not os.path.exists(filename):
        if verbose:
            print(f"❌ 文件不存在: {filename}")
        return None

    with open(filename, 'r', encoding='utf-8') as f:
        hex_string = f.read().strip()

    # 移除所有空格、换行和制表符
    hex_string = hex_string.replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '')

    # 转换为字节
    try:
        keystream = bytes.fromhex(hex_string)
        if verbose:
            print(f"✅ 密钥流大小: {len(keystream):,} bytes ({len(keystream) / 1024:.2f} KB)")
        return keystream
    except ValueError as e:
        if verbose:
            print(f"❌ 解析密钥流失败: {e}")
            print(f"   请确保文件内容为有效的十六进制字符串")
        return None


def read_keystream_from_string(hex_string, verbose=True):
    """
    从十六进制字符串读取密钥流

    Args:
        hex_string: 十六进制字符串
        verbose: 是否显示详细信息

    Returns:
        bytes: 密钥流数据，失败返回 None
    """
    if verbose:
        print(f"📝 从字符串解析密钥流...")

    # 移除所有空格、换行和制表符
    hex_string = hex_string.replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '')

    try:
        keystream = bytes.fromhex(hex_string)
        if verbose:
            print(f"✅ 密钥流大小: {len(keystream):,} bytes ({len(keystream) / 1024:.2f} KB)")
        return keystream
    except ValueError as e:
        if verbose:
            print(f"❌ 解析密钥流失败: {e}")
        return None


def decrypt_video(encrypted_file, keystream, output_file, verbose=True):
    """
    解密视频文件

    Args:
        encrypted_file: 加密视频文件路径
        keystream: 密钥流数据（bytes）
        output_file: 输出文件路径
        verbose: 是否显示详细信息

    Returns:
        bool: 解密是否成功
    """
    if verbose:
        print(f"\n📁 读取加密文件: {encrypted_file}")

    if not os.path.exists(encrypted_file):
        if verbose:
            print(f"❌ 文件不存在: {encrypted_file}")
        return False

    # 读取加密文件
    with open(encrypted_file, 'rb') as f:
        encrypted_data = f.read()

    file_size = len(encrypted_data)
    if verbose:
        print(f"   文件大小: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")

    # 确定需要解密的长度
    decrypt_len = min(len(keystream), len(encrypted_data))
    if verbose:
        print(f"\n🔓 开始解密...")
        print(f"   解密长度: {decrypt_len:,} bytes ({decrypt_len / 1024:.2f} KB)")

    # XOR 解密前 decrypt_len 字节
    if verbose:
        print(f"   进行 XOR 运算...")

    decrypted_chunk = bytes(a ^ b for a, b in zip(encrypted_data[:decrypt_len], keystream))

    # 拼接未加密的部分
    decrypted_full = decrypted_chunk + encrypted_data[decrypt_len:]

    # 验证解密
    if verbose:
        print(f"\n🔍 验证解密结果...")
        print(f"   前 32 字节: {' '.join(f'{b:02x}' for b in decrypted_full[:32])}")

    # 检查 MP4 文件签名
    is_valid_mp4 = False
    if b'ftyp' in decrypted_full[:32]:
        ftyp_offset = decrypted_full[:32].find(b'ftyp')
        is_valid_mp4 = True
        if verbose:
            print(f"   ✅✅✅ 找到 MP4 签名 'ftyp' @ 偏移 {ftyp_offset}")
            print(f"   🎬 这是一个有效的 MP4 文件！")
    else:
        if verbose:
            print(f"   ⚠️  未找到 'ftyp' 签名")
            print(f"   可能需要检查密钥流是否正确")

    # 保存解密后的文件
    if verbose:
        print(f"\n💾 保存解密文件: {output_file}")

    try:
        with open(output_file, 'wb') as f:
            f.write(decrypted_full)

        saved_size = os.path.getsize(output_file)
        if verbose:
            print(f"   ✅ 保存成功!")
            print(f"   文件大小: {saved_size:,} bytes ({saved_size / 1024 / 1024:.2f} MB)")

        return is_valid_mp4
    except Exception as e:
        if verbose:
            print(f"   ❌ 保存失败: {e}")
        return False


def interactive_mode():
    """交互式模式"""
    print("=" * 70)
    print("🎬 微信视频号解密工具 - 交互模式")
    print("=" * 70)
    print()

    # 密钥流文件
    keystream_file = "keystream_131072_bytes.txt"
    keystream = None

    if not os.path.exists(keystream_file):
        print(f"⚠️  未找到密钥流文件: {keystream_file}")
        print()
        print("请选择输入方式：")
        print("1. 输入密钥流文件路径")
        print("2. 直接粘贴十六进制密钥流")
        print("3. 退出")
        choice = input("\n请选择 (1/2/3): ").strip()

        if choice == "1":
            keystream_file = input("请输入密钥流文件路径: ").strip()
            if os.path.exists(keystream_file):
                keystream = read_keystream_from_file(keystream_file)
            else:
                print(f"❌ 文件不存在: {keystream_file}")
                return
        elif choice == "2":
            hex_string = input("请粘贴十六进制密钥流: ").strip()
            keystream = read_keystream_from_string(hex_string)
            if keystream:
                # 保存到文件
                with open(keystream_file, 'w') as f:
                    f.write(hex_string)
                print(f"✅ 已将密钥流保存到: {keystream_file}")
        else:
            print("❌ 用户取消操作")
            return
    else:
        keystream = read_keystream_from_file(keystream_file)

    if not keystream:
        print("❌ 无法读取密钥流")
        return

    if len(keystream) != 131072:
        print(f"⚠️  警告: 密钥流大小不是 131072 bytes (实际: {len(keystream):,} bytes)")
        confirm = input("是否继续? (y/n): ").strip().lower()
        if confirm != 'y':
            return

    # 加密文件
    encrypted_file = "wx_encrypted.mp4"
    if not os.path.exists(encrypted_file):
        encrypted_file = input(f"\n请输入加密视频文件路径: ").strip()
        if not os.path.exists(encrypted_file):
            print(f"❌ 文件不存在: {encrypted_file}")
            return

    # 输出文件
    default_output = "wx_decrypted.mp4"
    user_input = input(f"\n请输入输出文件名 (默认: {default_output}): ").strip()
    if user_input:
        output_file = user_input if user_input.endswith('.mp4') else f"{user_input}.mp4"
    else:
        output_file = default_output

    # 解密
    success = decrypt_video(encrypted_file, keystream, output_file)

    # 结果
    print()
    print("=" * 70)
    if success:
        print("🎉 解密完成！")
        print("=" * 70)
        print()
        print(f"📂 解密文件: {output_file}")
        print(f"📍 完整路径: {os.path.abspath(output_file)}")
        print()
        print("💡 可以使用以下命令播放视频:")
        print(f"   open {output_file}")
        print(f"   或")
        print(f"   mpv {output_file}")
    else:
        print("⚠️  解密完成，但可能存在问题")
        print("=" * 70)
        print()
        print("请检查：")
        print("1. 密钥流是否正确")
        print("2. 加密文件是否完整")
        print("3. decode_key 是否匹配此视频")
    print()


def cli_mode(args):
    """命令行模式"""
    print("=" * 70)
    print("🎬 微信视频号解密工具")
    print("=" * 70)
    print()

    # 读取密钥流
    keystream = None
    if args.keystream_file:
        keystream = read_keystream_from_file(args.keystream_file, verbose=not args.quiet)
    elif args.keystream_hex:
        keystream = read_keystream_from_string(args.keystream_hex, verbose=not args.quiet)

    if not keystream:
        print("❌ 无法读取密钥流")
        sys.exit(1)

    if len(keystream) != 131072 and not args.quiet:
        print(f"⚠️  警告: 密钥流大小不是 131072 bytes (实际: {len(keystream):,} bytes)")

    # 解密文件
    success = decrypt_video(
        args.input,
        keystream,
        args.output,
        verbose=not args.quiet
    )

    if success:
        if not args.quiet:
            print()
            print("=" * 70)
            print("🎉 解密完成！")
            print("=" * 70)
            print()
            print(f"📂 解密文件: {args.output}")
            print(f"📍 完整路径: {os.path.abspath(args.output)}")
            print()
    else:
        if not args.quiet:
            print()
            print("⚠️  解密完成，但可能存在问题")
            print("请检查密钥流和加密文件是否正确")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="微信视频号解密工具 - 使用 Isaac64 密钥流解密视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互模式（推荐新手使用）
  %(prog)s

  # 使用密钥流文件解密
  %(prog)s -i wx_encrypted.mp4 -k keystream_131072_bytes.txt -o wx_decrypted.mp4

  # 使用十六进制字符串解密
  %(prog)s -i encrypted.mp4 -H "0a1b2c3d..." -o decrypted.mp4

  # 静默模式
  %(prog)s -i encrypted.mp4 -k keystream.txt -o decrypted.mp4 -q

项目地址: https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption
作者: Evil0ctal
        """
    )

    parser.add_argument(
        '-i', '--input',
        help='加密视频文件路径'
    )

    parser.add_argument(
        '-o', '--output',
        help='输出文件路径（默认: wx_decrypted.mp4）'
    )

    parser.add_argument(
        '-k', '--keystream-file',
        help='密钥流文件路径（十六进制文本文件）'
    )

    parser.add_argument(
        '-H', '--keystream-hex',
        help='直接提供十六进制密钥流字符串'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='静默模式，只显示错误信息'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # 如果没有提供任何参数，进入交互模式
    if not args.input and not args.keystream_file and not args.keystream_hex:
        interactive_mode()
    else:
        # 验证必要参数
        if not args.input:
            parser.error("请提供加密视频文件路径 (-i/--input)")

        if not args.keystream_file and not args.keystream_hex:
            parser.error("请提供密钥流文件 (-k/--keystream-file) 或十六进制字符串 (-H/--keystream-hex)")

        if not args.output:
            args.output = "wx_decrypted.mp4"
            if not args.quiet:
                print(f"ℹ️  未指定输出文件，使用默认: {args.output}")

        cli_mode(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)
