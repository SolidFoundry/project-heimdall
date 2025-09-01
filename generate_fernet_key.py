#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成Fernet密钥的脚本
"""

from cryptography.fernet import Fernet
import base64

def generate_fernet_key():
    """生成一个有效的Fernet密钥"""
    key = Fernet.generate_key()
    return key.decode('utf-8')

def validate_key(key_str):
    """验证密钥是否有效"""
    try:
        # 检查是否是有效的base64
        decoded = base64.b64decode(key_str.encode('utf-8'))
        # 检查长度是否为32字节
        if len(decoded) == 32:
            return True, "有效的Fernet密钥"
        else:
            return False, f"密钥长度错误: {len(decoded)}字节，需要32字节"
    except Exception as e:
        return False, f"无效的base64编码: {e}"

if __name__ == "__main__":
    print("=== Fernet密钥生成器 ===")
    
    # 生成新密钥
    new_key = generate_fernet_key()
    print(f"生成的Fernet密钥: {new_key}")
    
    # 验证现有密钥
    print("\n验证现有密钥:")
    test_keys = [
        "EfYHFc3BFLOTfpgyC43t9XJnxItiH3zi",  # 当前.env中的密钥
        new_key,  # 新生成的密钥
    ]
    
    for key in test_keys:
        is_valid, message = validate_key(key)
        print(f"密钥 '{key[:20]}...': {message}")
        
    print(f"\n请在.env文件中使用以下密钥:")
    print(f"ENCRYPTION_KEY={new_key}")