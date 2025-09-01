#!/usr/bin/env python3
"""
企业页面快速测试脚本
验证修复后的功能是否正常
"""

import requests
import time


def quick_test():
    """快速测试企业页面功能"""
    print("🚀 企业页面快速测试")
    print("=" * 40)

    base_url = "http://localhost:8002"

    # 测试1: 健康检查
    print("1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            print("   ✅ 健康检查正常")
        else:
            print(f"   ❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 健康检查异常: {e}")
        return False

    # 测试2: 仪表板统计
    print("2. 测试仪表板统计...")
    try:
        response = requests.get(f"{base_url}/api/v1/memory/dashboard-stats")
        if response.status_code == 200:
            data = response.json()
            overview = data.get("overview", {})
            print(f"   ✅ 仪表板统计正常")
            print(f"      产品: {overview.get('total_products')}")
            print(f"      用户: {overview.get('total_users')}")
            print(f"      行为: {overview.get('total_behaviors')}")
        else:
            print(f"   ❌ 仪表板统计失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 仪表板统计异常: {e}")
        return False

    # 测试3: 企业页面访问
    print("3. 测试企业页面...")
    try:
        response = requests.get(f"{base_url}/enterprise")
        if response.status_code == 200:
            content = response.text
            required_elements = [
                'id="system-status"',
                'id="total-products"',
                'id="total-users"',
                'id="total-behaviors"',
                "enterprise.js",
                "enterprise.css",
            ]

            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)

            if not missing_elements:
                print("   ✅ 企业页面结构完整")
            else:
                print(f"   ⚠️ 缺少元素: {missing_elements}")
        else:
            print(f"   ❌ 企业页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 企业页面访问异常: {e}")
        return False

    print("\n" + "=" * 40)
    print("✅ 快速测试完成！")
    print("\n🔧 下一步操作:")
    print("1. 访问: http://localhost:8002/enterprise")
    print("2. 按 Ctrl+F5 强制刷新")
    print("3. 检查系统状态是否显示'在线'")
    print("4. 测试刷新按钮功能")
    print("5. 测试菜单点击功能")

    return True


if __name__ == "__main__":
    quick_test()
