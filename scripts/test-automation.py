#!/usr/bin/env python3
"""
测试自动化系统的各个组件
"""

import os
import sys
import re
import requests
from bs4 import BeautifulSoup

def test_makefile_parsing():
    """测试Makefile解析功能"""
    print("🧪 测试Makefile解析...")
    
    makefile_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'golang', 'Makefile')
    
    if not os.path.exists(makefile_path):
        print("❌ Makefile不存在")
        return False
    
    with open(makefile_path, 'r') as f:
        content = f.read()
    
    major_minor_match = re.search(r'GO_VERSION_MAJOR_MINOR:=(\d+\.\d+)', content)
    patch_match = re.search(r'GO_VERSION_PATCH:=(\d+)', content)
    hash_match = re.search(r'PKG_HASH:=([a-f0-9]{64})', content)
    
    if not major_minor_match:
        print("❌ 无法解析GO_VERSION_MAJOR_MINOR")
        return False
    
    if not patch_match:
        print("❌ 无法解析GO_VERSION_PATCH")
        return False
    
    if not hash_match:
        print("❌ 无法解析PKG_HASH")
        return False
    
    version = f"{major_minor_match.group(1)}.{patch_match.group(1)}"
    hash_value = hash_match.group(1)
    
    print(f"✅ 成功解析版本: {version}")
    print(f"✅ 成功解析哈希: {hash_value[:16]}...")
    return True

def test_go_website_access():
    """测试Go官网访问"""
    print("\n🧪 测试Go官网访问...")
    
    try:
        response = requests.get('https://go.dev/dl/', timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找版本信息
        versions_found = 0
        for div in soup.find_all('div', class_='toggle'):
            version_text = div.get('id', '')
            if version_text.startswith('go'):
                versions_found += 1
                if versions_found == 1:  # 显示第一个版本
                    version = version_text[2:]
                    print(f"✅ 找到最新版本: {version}")
        
        if versions_found == 0:
            print("❌ 未找到任何版本信息")
            return False
        
        print(f"✅ 总共找到 {versions_found} 个版本")
        return True
        
    except Exception as e:
        print(f"❌ 访问Go官网失败: {e}")
        return False

def test_source_download():
    """测试源码包下载 (仅测试HEAD请求)"""
    print("\n🧪 测试源码包可访问性...")
    
    # 使用当前版本进行测试
    makefile_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'golang', 'Makefile')
    
    with open(makefile_path, 'r') as f:
        content = f.read()
    
    major_minor_match = re.search(r'GO_VERSION_MAJOR_MINOR:=(\d+\.\d+)', content)
    patch_match = re.search(r'GO_VERSION_PATCH:=(\d+)', content)
    
    if not major_minor_match or not patch_match:
        print("❌ 无法解析当前版本")
        return False
    
    version = f"{major_minor_match.group(1)}.{patch_match.group(1)}"
    
    try:
        url = f"https://dl.google.com/go/go{version}.src.tar.gz"
        response = requests.head(url, timeout=10)
        response.raise_for_status()
        
        content_length = response.headers.get('content-length')
        if content_length:
            size_mb = int(content_length) / (1024 * 1024)
            print(f"✅ 源码包可访问: {url}")
            print(f"✅ 文件大小: {size_mb:.1f}MB")
        else:
            print(f"✅ 源码包可访问: {url}")
        
        return True
        
    except Exception as e:
        print(f"❌ 源码包访问失败: {e}")
        return False

def test_script_syntax():
    """测试脚本语法"""
    print("\n🧪 测试脚本语法...")
    
    script_path = os.path.join(os.path.dirname(__file__), 'update-golang.py')
    
    try:
        with open(script_path, 'r') as f:
            code = f.read()
        
        compile(code, script_path, 'exec')
        print("✅ update-golang.py 语法正确")
        return True
        
    except SyntaxError as e:
        print(f"❌ update-golang.py 语法错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 检查脚本时出错: {e}")
        return False

def main():
    """运行所有测试"""
    print("🚀 开始测试自动化系统组件...\n")
    
    tests = [
        ("Makefile解析", test_makefile_parsing),
        ("Go官网访问", test_go_website_access),
        ("源码包访问", test_source_download),
        ("脚本语法", test_script_syntax),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！自动化系统准备就绪。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关组件。")
        return 1

if __name__ == '__main__':
    sys.exit(main())