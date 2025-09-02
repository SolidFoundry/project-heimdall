#!/usr/bin/env python
"""
生成安全密钥的脚本
用于生成各种加密密钥和随机字符串
"""

import secrets
import string
from cryptography.fernet import Fernet

def generate_jwt_secret():
    """生成JWT密钥"""
    print("=== JWT Secret Key ===")
    jwt_secret = secrets.token_urlsafe(32)
    print(f"SECRET_KEY={jwt_secret}")
    print(f"长度: {len(jwt_secret)} 字符")
    print()

def generate_encryption_key():
    """生成Fernet加密密钥"""
    print("=== Fernet Encryption Key ===")
    key = Fernet.generate_key()
    print(f"ENCRYPTION_KEY={key.decode()}")
    print(f"长度: {len(key)} 字节")
    print()

def generate_database_password(length=16):
    """生成数据库密码"""
    print("=== Database Password ===")
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    print(f"DATABASE_PASSWORD={password}")
    print(f"长度: {len(password)} 字符")
    print("注意: 请确保密码符合PostgreSQL的密码要求")
    print()

def generate_api_key():
    """生成API密钥（示例格式）"""
    print("=== API Key (示例格式) ===")
    # 生成类似OpenAI API密钥的格式
    prefix = "sk-"
    key_part = secrets.token_urlsafe(32)
    api_key = f"{prefix}{key_part}"
    print(f"API_KEY示例={api_key}")
    print("注意: 这只是示例格式，请使用从服务提供商获取的真实API密钥")
    print()

def generate_random_string(length=32, purpose="general"):
    """生成通用随机字符串"""
    print(f"=== Random String ({purpose}) ===")
    random_string = secrets.token_urlsafe(length)
    print(f"随机字符串: {random_string}")
    print(f"长度: {len(random_string)} 字符")
    print()

def main():
    """主函数"""
    print("Project Heimdall - 安全密钥生成工具\n")
    print("=" * 50)
    print()
    
    # 生成各种密钥
    generate_jwt_secret()
    generate_encryption_key()
    generate_database_password()
    generate_api_key()
    generate_random_string(32, "session_secret")
    generate_random_string(16, "csrf_token")
    
    print("=" * 50)
    print("\n使用说明:")
    print("1. 将生成的密钥复制到你的 .env 文件中")
    print("2. 每个环境（开发、测试、生产）都应该使用不同的密钥")
    print("3. 定期轮换密钥以提高安全性")
    print("4. 将 .env 文件添加到 .gitignore 中")
    print("5. 永远不要将密钥提交到版本控制系统")
    print("\n警告: 请妥善保管生成的密钥，泄露可能导致安全风险！")

if __name__ == "__main__":
    main()