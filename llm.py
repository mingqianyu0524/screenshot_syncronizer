from google import genai
from PIL import Image
import anthropic
import base64
import os
from dotenv import load_dotenv

load_dotenv()

# 获取配置
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "claude").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
    print("⚠️ 警告: 未找到 GEMINI_API_KEY 环境变量")
elif LLM_PROVIDER == "claude" and not ANTHROPIC_API_KEY:
    print("⚠️ 警告: 未找到 ANTHROPIC_API_KEY 环境变量")


def _analyze_image_gemini(image_path, prompt):
    """
    使用新的 google-genai SDK 发送图片给 Gemini
    """
    print(f"🤖 正在请求 Gemini 分析图片: {image_path}...")

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        img = Image.open(image_path)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[img, prompt]
        )

        print("✅ Gemini 回复接收成功！")
        return response.text

    except Exception as e:
        print(f"❌ Gemini API 调用失败: {e}")
        return f"Error: {str(e)}"


def _analyze_image_claude(image_path, prompt):
    """
    使用 Anthropic SDK 发送图片给 Claude
    """
    print(f"🤖 正在请求 Claude 分析图片: {image_path}...")

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        # 读取图片并转为 base64
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
        )

        print("✅ Claude 回复接收成功！")
        return response.content[0].text

    except Exception as e:
        print(f"❌ Claude API 调用失败: {e}")
        return f"Error: {str(e)}"


def analyze_image(image_path, prompt="Explain what is in this image"):
    """
    根据 LLM_PROVIDER 环境变量分发到对应的 API
    """
    if not os.path.exists(image_path):
        return "Error: Image file not found."

    if LLM_PROVIDER == "gemini":
        return _analyze_image_gemini(image_path, prompt)
    else:
        return _analyze_image_claude(image_path, prompt)


# 测试代码
if __name__ == "__main__":
    # 确保你有一张测试图片，或者注释掉这行
    print(analyze_image("resources/screenshot_20260206_003623.png", "Describe it."))
    pass
