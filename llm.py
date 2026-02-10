from google import genai
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

# 1. 获取 API Key
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("⚠️ 警告: 未找到 GEMINI_API_KEY 环境变量")


def analyze_image(image_path, prompt="Explain what is in this image"):
    """
    使用新的 google-genai SDK 发送图片给 Gemini
    """
    print(f"🤖 正在请求 Gemini 分析图片: {image_path}...")

    if not os.path.exists(image_path):
        return "Error: Image file not found."

    try:
        # 2. 初始化客户端 (新版写法)
        client = genai.Client(api_key=API_KEY)

        # 3. 加载图片
        img = Image.open(image_path)

        # 4. 发送请求 (注意这里的 API 变化: models.generate_content)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[img, prompt]
        )

        print("✅ Gemini 回复接收成功！")

        # 5. 返回文本
        return response.text

    except Exception as e:
        print(f"❌ Gemini API 调用失败: {e}")
        return f"Error: {str(e)}"


# 测试代码
if __name__ == "__main__":
    # 确保你有一张测试图片，或者注释掉这行
    print(analyze_image("resources/screenshot_20260206_003623.png", "Describe it."))
    pass
