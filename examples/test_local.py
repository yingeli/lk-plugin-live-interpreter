#!/usr/bin/env python3
"""
本地测试脚本 - 用于快速验证 Azure Live Interpreter 插件安装和配置

这个脚本会:
1. 检查所有必需的环境变量
2. 验证 Azure Speech Service 连接
3. 验证 LiveKit 连接
4. 测试插件基本功能

使用方法:
    python examples/test_local.py
"""

import asyncio
import os
import sys
from typing import Optional

# 添加项目路径到 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def print_header(text: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_success(text: str):
    """打印成功消息"""
    print(f"✓ {text}")


def print_error(text: str):
    """打印错误消息"""
    print(f"✗ {text}")


def print_info(text: str):
    """打印信息"""
    print(f"ℹ {text}")


def check_env_var(name: str, required: bool = True) -> Optional[str]:
    """检查环境变量"""
    value = os.environ.get(name)
    if value:
        # 隐藏敏感信息
        if "KEY" in name or "SECRET" in name:
            display_value = value[:8] + "..." if len(value) > 8 else "***"
        else:
            display_value = value
        print_success(f"{name}: {display_value}")
        return value
    else:
        if required:
            print_error(f"{name}: 未设置 (必需)")
        else:
            print_info(f"{name}: 未设置 (可选)")
        return None


async def test_azure_connection(subscription_key: str, region: str) -> bool:
    """测试 Azure Speech Service 连接"""
    try:
        import azure.cognitiveservices.speech as speechsdk

        speech_config = speechsdk.SpeechConfig(
            subscription=subscription_key, region=region
        )
        print_success("Azure Speech Service 配置创建成功")

        # 尝试创建语音识别器来验证凭证
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=False)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )
        print_success("Azure Speech Service 连接验证成功")
        return True

    except ImportError:
        print_error("azure-cognitiveservices-speech 未安装")
        print_info("运行: pip install azure-cognitiveservices-speech")
        return False
    except Exception as e:
        print_error(f"Azure 连接失败: {e}")
        return False


async def test_livekit_connection(url: str, api_key: str, api_secret: str) -> bool:
    """测试 LiveKit 连接"""
    try:
        from livekit import api

        # 创建 LiveKit API 客户端
        lk_api = api.LiveKitAPI(url, api_key, api_secret)
        print_success("LiveKit API 客户端创建成功")

        # 尝试列出房间（验证连接）
        try:
            rooms = await lk_api.room.list_rooms(api.ListRoomsRequest())
            print_success(f"LiveKit 连接验证成功 (当前房间数: {len(rooms.rooms)})")
            return True
        except Exception as e:
            print_error(f"LiveKit 连接失败: {e}")
            print_info("请检查 LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET")
            return False

    except ImportError:
        print_error("livekit 或 livekit-api 未安装")
        print_info("运行: pip install livekit livekit-api")
        return False
    except Exception as e:
        print_error(f"LiveKit 初始化失败: {e}")
        return False


async def test_plugin_import() -> bool:
    """测试插件导入"""
    try:
        from livekit.plugins import azure

        print_success("Azure 插件导入成功")

        # 检查必需的类是否存在
        if hasattr(azure, "realtime"):
            print_success("realtime 模块存在")
        else:
            print_error("realtime 模块不存在")
            return False

        if hasattr(azure.realtime, "LiveInterpreterModel"):
            print_success("LiveInterpreterModel 类存在")
        else:
            print_error("LiveInterpreterModel 类不存在")
            return False

        return True

    except ImportError as e:
        print_error(f"插件导入失败: {e}")
        print_info("请确保插件已安装: cd livekit-plugins/livekit-plugins-azure && pip install -e .")
        return False
    except Exception as e:
        print_error(f"插件测试失败: {e}")
        return False


async def test_plugin_instantiation() -> bool:
    """测试插件实例化"""
    try:
        from livekit.plugins import azure

        # 尝试创建模型实例
        model = azure.realtime.LiveInterpreterModel(
            target_languages=["fr", "es"],
        )
        print_success("LiveInterpreterModel 实例创建成功")

        # 检查配置
        print_info(f"目标语言: {model._target_languages}")
        print_info(f"采样率: {model._sample_rate}")
        print_info(f"使用个人语音: {model._use_personal_voice}")

        return True

    except Exception as e:
        print_error(f"插件实例化失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print_header("Azure Live Interpreter 插件本地测试")

    all_passed = True

    # 步骤 1: 检查环境变量
    print_header("步骤 1: 检查环境变量")

    azure_key = check_env_var("AZURE_SPEECH_KEY", required=True)
    azure_region = check_env_var("AZURE_SPEECH_REGION", required=True)
    livekit_url = check_env_var("LIVEKIT_URL", required=True)
    livekit_api_key = check_env_var("LIVEKIT_API_KEY", required=True)
    livekit_api_secret = check_env_var("LIVEKIT_API_SECRET", required=True)
    check_env_var("AZURE_SPEAKER_PROFILE_ID", required=False)

    if not all([azure_key, azure_region, livekit_url, livekit_api_key, livekit_api_secret]):
        print_error("\n必需的环境变量未设置！")
        print_info("请创建 .env 文件并设置所有必需的环境变量")
        print_info("参考: LOCAL_TESTING.md")
        return 1

    # 步骤 2: 测试 Azure 连接
    print_header("步骤 2: 测试 Azure Speech Service 连接")
    if not await test_azure_connection(azure_key, azure_region):
        all_passed = False
        print_error("Azure 连接测试失败")
    else:
        print_success("Azure 连接测试通过")

    # 步骤 3: 测试 LiveKit 连接
    print_header("步骤 3: 测试 LiveKit 连接")
    if not await test_livekit_connection(livekit_url, livekit_api_key, livekit_api_secret):
        all_passed = False
        print_error("LiveKit 连接测试失败")
    else:
        print_success("LiveKit 连接测试通过")

    # 步骤 4: 测试插件导入
    print_header("步骤 4: 测试插件导入")
    if not await test_plugin_import():
        all_passed = False
        print_error("插件导入测试失败")
    else:
        print_success("插件导入测试通过")

    # 步骤 5: 测试插件实例化
    print_header("步骤 5: 测试插件实例化")
    if not await test_plugin_instantiation():
        all_passed = False
        print_error("插件实例化测试失败")
    else:
        print_success("插件实例化测试通过")

    # 总结
    print_header("测试总结")

    if all_passed:
        print_success("所有测试通过！✨")
        print_info("\n您现在可以运行完整的示例:")
        print_info("  python examples/simple_interpreter.py")
        print_info("  python examples/multi_language_meeting.py")
        print_info("\n更多信息请参考 LOCAL_TESTING.md")
        return 0
    else:
        print_error("部分测试失败")
        print_info("\n请检查上述错误信息并修复问题")
        print_info("参考文档: LOCAL_TESTING.md")
        return 1


if __name__ == "__main__":
    # 加载 .env 文件（如果存在）
    try:
        from dotenv import load_dotenv

        load_dotenv()
        print_info("已加载 .env 文件")
    except ImportError:
        print_info("python-dotenv 未安装，跳过 .env 文件加载")
        print_info("提示: pip install python-dotenv")

    # 运行测试
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
