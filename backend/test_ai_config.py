#!/usr/bin/env python3
"""
AI 配置样本测试验证脚本
"""
import requests
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

# 测试用的 token（需要先登录获取）
TOKEN = None


def login_as_admin():
    """登录获取 token"""
    global TOKEN
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        data = response.json()
        TOKEN = data["data"]["access_token"]
        print(f"✓ 登录成功，获取 token")
        return True
    else:
        print(f"✗ 登录失败: {response.text}")
        return False


def get_headers():
    """获取请求头"""
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }


def test_list_configs():
    """测试：获取配置列表"""
    print("\n=== 测试：获取配置列表 ===")
    response = requests.get(
        f"{BASE_URL}/ai-configs",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        configs = data["data"]
        print(f"✓ 获取配置列表成功，共 {len(configs)} 条")

        for config in configs:
            print(f"  - ID: {config['id']}, Name: {config['name']}")
            print(f"    API Style: {config['api_style']}")
            print(f"    API Key Masked: {config.get('api_key_masked', 'N/A')}")
            print(f"    Has API Key: {config.get('has_api_key', 'N/A')}")
            print(f"    PDF Strategy: {config.get('pdf_strategy', 'N/A')}")

        return configs
    else:
        print(f"✗ 获取配置列表失败: {response.text}")
        return []


def test_connection(config_id):
    """测试：测试连接"""
    print(f"\n=== 测试：测试连接 (config_id={config_id}) ===")
    response = requests.post(
        f"{BASE_URL}/ai-configs/test-connection?config_id={config_id}",
        headers=get_headers()
    )

    if response.status_code == 200:
        data = response.json()
        result = data["data"]
        print(f"✓ 测试连接完成")
        print(f"  Success: {result['success']}")
        print(f"  Message: {result['message']}")
        print(f"  Latency: {result.get('latency_ms', 'N/A')} ms")
        print(f"  Request Path: {result.get('request_path', 'N/A')}")
        print(f"  Status Code: {result.get('status_code', 'N/A')}")
        return result
    else:
        print(f"✗ 测试连接失败: {response.text}")
        return None


def test_image_sample(config_id, image_path, invoice_type="vat_normal"):
    """测试：图片样本测试"""
    print(f"\n=== 测试：图片样本测试 (config_id={config_id}) ===")

    if not Path(image_path).exists():
        print(f"✗ 图片文件不存在: {image_path}")
        return None

    with open(image_path, 'rb') as f:
        files = {
            'file': (Path(image_path).name, f, 'image/jpeg')
        }
        data = {
            'invoice_type': invoice_type
        }
        headers = {
            "Authorization": f"Bearer {TOKEN}"
        }

        response = requests.post(
            f"{BASE_URL}/ai-configs/{config_id}/sample-test",
            headers=headers,
            files=files,
            data=data
        )

    if response.status_code == 200:
        result = response.json()["data"]
        print(f"✓ 图片样本测试完成")
        print(f"  Test Mode: {result['test_mode']}")
        print(f"  File Name: {result['file_name']}")
        print(f"  Success: {result['result']['success']}")
        print(f"  Latency: {result['result']['latency_ms']} ms")
        print(f"  Request Path: {result['result']['request_path']}")
        print(f"  Execution Path: {result['result']['execution_path']}")

        if result['result']['success']:
            print(f"  Structured Result: {json.dumps(result['result']['structured_result'], ensure_ascii=False, indent=2)[:200]}...")
        else:
            print(f"  Error: {result['result']['error_message']}")

        return result
    else:
        print(f"✗ 图片样本测试失败: {response.text}")
        return None


def test_pdf_sample(config_id, pdf_path, invoice_type="vat_normal"):
    """测试：PDF 样本测试（双策略）"""
    print(f"\n=== 测试：PDF 样本测试 (config_id={config_id}) ===")

    if not Path(pdf_path).exists():
        print(f"✗ PDF 文件不存在: {pdf_path}")
        return None

    with open(pdf_path, 'rb') as f:
        files = {
            'file': (Path(pdf_path).name, f, 'application/pdf')
        }
        data = {
            'invoice_type': invoice_type
        }
        headers = {
            "Authorization": f"Bearer {TOKEN}"
        }

        response = requests.post(
            f"{BASE_URL}/ai-configs/{config_id}/sample-test",
            headers=headers,
            files=files,
            data=data
        )

    if response.status_code == 200:
        result = response.json()["data"]
        print(f"✓ PDF 样本测试完成")
        print(f"  Test Mode: {result['test_mode']}")
        print(f"  File Name: {result['file_name']}")

        # Direct PDF 结果
        direct = result['direct_pdf_result']
        print(f"\n  Direct PDF:")
        print(f"    Success: {direct['success']}")
        print(f"    Latency: {direct['latency_ms']} ms")
        print(f"    Request Path: {direct['request_path']}")
        print(f"    Execution Path: {direct['execution_path']}")
        if not direct['success']:
            print(f"    Error: {direct['error_message']}")

        # Convert to Images 结果
        convert = result['convert_to_images_result']
        print(f"\n  Convert to Images:")
        print(f"    Success: {convert['success']}")
        print(f"    Latency: {convert['latency_ms']} ms")
        print(f"    Request Path: {convert['request_path']}")
        print(f"    Execution Path: {convert['execution_path']}")
        if not convert['success']:
            print(f"    Error: {convert['error_message']}")

        # 推荐策略
        print(f"\n  Recommended Strategy: {result['recommended_strategy']}")
        print(f"  Recommendation Reason: {result['recommendation_reason']}")

        return result
    else:
        print(f"✗ PDF 样本测试失败: {response.text}")
        return None


def test_update_pdf_strategy(config_id, strategy):
    """测试：更新 PDF 策略"""
    print(f"\n=== 测试：更新 PDF 策略 (config_id={config_id}, strategy={strategy}) ===")
    response = requests.post(
        f"{BASE_URL}/ai-configs/{config_id}/pdf-strategy",
        headers=get_headers(),
        json={"pdf_strategy": strategy}
    )

    if response.status_code == 200:
        print(f"✓ 更新 PDF 策略成功")
        return True
    else:
        print(f"✗ 更新 PDF 策略失败: {response.text}")
        return False


def main():
    """主测试流程"""
    print("=" * 60)
    print("AI 配置样本测试验证")
    print("=" * 60)

    # 1. 登录
    if not login_as_admin():
        sys.exit(1)

    # 2. 获取配置列表
    configs = test_list_configs()
    if not configs:
        print("\n✗ 没有可用的配置")
        sys.exit(1)

    # 选择一个配置进行测试
    test_config_id = None
    for config in configs:
        if config['api_style'] in ['openai_chat_completions', 'anthropic_messages']:
            test_config_id = config['id']
            print(f"\n选择配置 ID {test_config_id} 进行测试")
            break

    if not test_config_id:
        print("\n✗ 没有找到合适的配置")
        sys.exit(1)

    # 3. 测试连接
    test_connection(test_config_id)

    # 4. 图片样本测试（需要提供真实图片路径）
    # test_image_sample(test_config_id, "/path/to/test/image.jpg")

    # 5. PDF 样本测试（需要提供真实 PDF 路径）
    # test_pdf_sample(test_config_id, "/path/to/test/invoice.pdf")

    # 6. 更新 PDF 策略
    # test_update_pdf_strategy(test_config_id, "direct_pdf")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
