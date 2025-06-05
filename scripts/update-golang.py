#!/usr/bin/env python3
"""
Golang版本更新脚本
用于自动更新Makefile中的Go版本和哈希值

使用方法:
    python3 update-golang.py [version]
    
示例:
    python3 update-golang.py 1.24.6  # 更新到指定版本
    python3 update-golang.py          # 更新到最新版本
"""

import re
import requests
import sys
import hashlib
import os
from bs4 import BeautifulSoup
import argparse

def get_current_version():
    """从Makefile读取当前版本"""
    makefile_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'golang', 'Makefile')
    
    if not os.path.exists(makefile_path):
        raise FileNotFoundError(f"Makefile not found at {makefile_path}")
    
    with open(makefile_path, 'r') as f:
        content = f.read()
    
    major_minor_match = re.search(r'GO_VERSION_MAJOR_MINOR:=(\d+\.\d+)', content)
    patch_match = re.search(r'GO_VERSION_PATCH:=(\d+)', content)
    
    if major_minor_match and patch_match:
        return f"{major_minor_match.group(1)}.{patch_match.group(1)}"
    return None

def get_latest_version():
    """从pkg.go.dev获取最新稳定版本"""
    try:
        print("正在从pkg.go.dev获取最新Go版本...")
        response = requests.get('https://pkg.go.dev/std?tab=versions', timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找版本列表中的第一个稳定版本（不包含rc、beta等）
        version_links = soup.find_all('a', href=re.compile(r'/std@go\d+\.\d+\.\d+$'))
        
        for link in version_links:
            href = link.get('href', '')
            # 提取版本号，格式如 /std@go1.24.5
            version_match = re.search(r'/std@go(\d+\.\d+\.\d+)$', href)
            if version_match:
                version = version_match.group(1)
                # 确保不包含rc、beta等标识
                if not any(x in version.lower() for x in ['beta', 'rc', 'alpha', 'dev']):
                    print(f"找到稳定版本: {version}")
                    return version
        
        # 如果上面的方法失败，尝试查找版本文本
        print("尝试备用方法查找版本...")
        version_elements = soup.find_all(text=re.compile(r'go\d+\.\d+\.\d+$'))
        for element in version_elements:
            version_match = re.search(r'go(\d+\.\d+\.\d+)$', element.strip())
            if version_match:
                version = version_match.group(1)
                if not any(x in version.lower() for x in ['beta', 'rc', 'alpha', 'dev']):
                    print(f"从文本中找到稳定版本: {version}")
                    return version
        
        return None
    except Exception as e:
        print(f"获取最新版本失败: {e}")
        return None

def get_source_hash(version):
    """获取源码包的SHA256哈希"""
    try:
        print(f"正在下载Go {version}源码包以计算哈希...")
        url = f"https://dl.google.com/go/go{version}.src.tar.gz"
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        
        sha256_hash = hashlib.sha256()
        total_size = 0
        for chunk in response.iter_content(chunk_size=8192):
            sha256_hash.update(chunk)
            total_size += len(chunk)
            if total_size % (1024 * 1024) == 0:  # 每MB显示进度
                print(f"已下载: {total_size // (1024 * 1024)}MB")
        
        hash_value = sha256_hash.hexdigest()
        print(f"下载完成，文件大小: {total_size // (1024 * 1024)}MB")
        return hash_value
    except Exception as e:
        print(f"下载源码包失败: {e}")
        return None

def update_makefile(target_version, new_hash):
    """更新Makefile"""
    makefile_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'golang', 'Makefile')
    
    # 解析版本号
    version_parts = target_version.split('.')
    if len(version_parts) != 3:
        raise ValueError(f"无效的版本格式: {target_version}")
    
    major_minor = f"{version_parts[0]}.{version_parts[1]}"
    patch = version_parts[2]
    
    # 读取原文件
    with open(makefile_path, 'r') as f:
        content = f.read()
    
    # 备份原文件
    backup_path = makefile_path + '.bak'
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"已备份原文件到: {backup_path}")
    
    # 更新内容
    content = re.sub(r'GO_VERSION_MAJOR_MINOR:=.*', f'GO_VERSION_MAJOR_MINOR:={major_minor}', content)
    content = re.sub(r'GO_VERSION_PATCH:=.*', f'GO_VERSION_PATCH:={patch}', content)
    content = re.sub(r'PKG_HASH:=.*', f'PKG_HASH:={new_hash}', content)
    
    # 写入更新后的内容
    with open(makefile_path, 'w') as f:
        f.write(content)
    
    print(f"已更新Makefile:")
    print(f"  GO_VERSION_MAJOR_MINOR: {major_minor}")
    print(f"  GO_VERSION_PATCH: {patch}")
    print(f"  PKG_HASH: {new_hash}")

def main():
    parser = argparse.ArgumentParser(description='更新Golang版本')
    parser.add_argument('version', nargs='?', help='目标版本 (例如: 1.24.6)')
    parser.add_argument('--dry-run', action='store_true', help='仅显示将要进行的更改，不实际修改文件')
    args = parser.parse_args()
    
    try:
        # 获取当前版本
        current_version = get_current_version()
        if current_version:
            print(f"当前版本: {current_version}")
        else:
            print("无法读取当前版本")
            return 1
        
        # 确定目标版本
        if args.version:
            target_version = args.version
            print(f"目标版本: {target_version} (手动指定)")
        else:
            target_version = get_latest_version()
            if not target_version:
                print("无法获取最新版本")
                return 1
            print(f"目标版本: {target_version} (最新版本)")
        
        # 检查是否需要更新
        if current_version == target_version:
            print("版本已是最新，无需更新")
            return 0
        
        # 获取新版本的哈希
        new_hash = get_source_hash(target_version)
        if not new_hash:
            print("无法获取源码包哈希")
            return 1
        
        print(f"新版本哈希: {new_hash}")
        
        if args.dry_run:
            print("\n[DRY RUN] 将要进行的更改:")
            version_parts = target_version.split('.')
            major_minor = f"{version_parts[0]}.{version_parts[1]}"
            patch = version_parts[2]
            print(f"  GO_VERSION_MAJOR_MINOR: {major_minor}")
            print(f"  GO_VERSION_PATCH: {patch}")
            print(f"  PKG_HASH: {new_hash}")
            print("使用 --dry-run 参数，未实际修改文件")
            return 0
        
        # 更新Makefile
        update_makefile(target_version, new_hash)
        print(f"\n✅ 成功更新Golang从 {current_version} 到 {target_version}")
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())