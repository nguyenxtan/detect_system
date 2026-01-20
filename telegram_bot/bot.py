"""Telegram Bot for defect reporting"""
import os
import sys
import asyncio
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    print("Error: TELEGRAM_BOT_TOKEN not found in environment variables")
    sys.exit(1)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
🏭 **Hệ Thống Nhận Dạng Lỗi Sản Phẩm - PU/PE Manufacturing**

Xin chào! Tôi là trợ lý AI giúp bạn nhận dạng lỗi sản phẩm.

**Các lệnh:**
/start - Bắt đầu
/report - Báo cáo lỗi
/history - Xem lịch sử 10 báo cáo gần nhất
/help - Hướng dẫn sử dụng

**Cách sử dụng:**
1. Gửi ảnh lỗi sản phẩm trực tiếp
2. Bot sẽ phân tích và trả về:
   - Loại lỗi
   - Mô tả chuẩn QC
   - Ảnh tham khảo
   - Độ tin cậy (%)

Hãy gửi ảnh để bắt đầu! 📸
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📖 **Hướng dẫn sử dụng:**

**1. Gửi ảnh lỗi sản phẩm:**
   - Chụp ảnh rõ nét, đủ ánh sáng
   - Gửi trực tiếp cho bot
   - Bot sẽ tự động phân tích

**2. Các loại lỗi:**
   - Cấn (dents, indentations)
   - Rách (tears, cuts)
   - Nhăn (wrinkles)
   - Phồng (bubbles, blisters)
   - OK (không có lỗi)

**3. Kết quả:**
   Bot trả về:
   - Loại lỗi
   - Mô tả chi tiết theo chuẩn QC
   - Ảnh tham khảo
   - % độ tin cậy

**4. Lưu ý:**
   - Một ảnh mỗi lần
   - Kích thước < 10MB
   - Format: JPG, PNG

Cần hỗ trợ? Liên hệ QC team.
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /report command"""
    await update.message.reply_text(
        "📸 Vui lòng gửi ảnh lỗi sản phẩm cần kiểm tra.\n\n"
        "Hãy chụp ảnh rõ nét và gửi vào đây."
    )


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command"""
    user_id = str(update.effective_user.id)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/api/defects/incidents/public",
                params={"user_id": user_id, "limit": 10}
            )

        if response.status_code == 200:
            incidents = response.json()

            if not incidents:
                await update.message.reply_text("📋 Bạn chưa có báo cáo nào.")
                return

            message = "📋 **10 báo cáo gần nhất của bạn:**\n\n"
            for idx, incident in enumerate(incidents, 1):
                created_at = incident.get('created_at', 'N/A')
                defect_type = incident.get('predicted_defect_type', 'Unknown')
                confidence = incident.get('confidence', 0)
                message += f"{idx}. `{defect_type}` - {confidence:.0%} - {created_at[:10]}\n"

            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Không thể lấy lịch sử. Vui lòng thử lại sau.")

    except Exception as e:
        print(f"Error fetching history: {e}")
        await update.message.reply_text("❌ Lỗi kết nối API. Vui lòng thử lại sau.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages"""
    print(f"📸 [DEBUG] handle_photo called! User: {update.effective_user.id}")
    await update.message.reply_text("🔍 Đang phân tích ảnh... Vui lòng đợi.")

    try:
        # Get the largest photo
        photo = update.message.photo[-1]
        photo_file = await photo.get_file()

        # Download photo
        photo_bytes = await photo_file.download_as_bytearray()

        # Send to API for matching
        # Timeout config for first-time CLIP model loading (can take 5-7 minutes)
        timeout = httpx.Timeout(
            timeout=600.0,    # Total timeout: 10 minutes
            connect=60.0,     # Connection timeout: 1 minute
            read=600.0,       # Read timeout: 10 minutes (for CLIP loading)
            write=60.0,       # Write timeout: 1 minute
            pool=60.0         # Pool timeout: 1 minute
        )

        print(f"📤 [DEBUG] Sending request to {API_BASE_URL}/api/defects/match")
        print(f"📤 [DEBUG] Image size: {len(photo_bytes)} bytes")

        async with httpx.AsyncClient(timeout=timeout) as client:
            files = {"image": ("image.jpg", bytes(photo_bytes), "image/jpeg")}
            data = {"user_id": str(update.effective_user.id)}
            response = await client.post(
                f"{API_BASE_URL}/api/defects/match",
                files=files,
                data=data
            )

        print(f"✅ [DEBUG] Response received: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            defect_profile = result['defect_profile']
            confidence = result['confidence']

            # Format response
            message = f"""
✅ **Kết quả nhận dạng:**

**Loại lỗi:** `{defect_profile['defect_type']}`
**Tên:** {defect_profile['defect_title']}
**Độ tin cậy:** {confidence:.0%}

**Mô tả chuẩn QC:**
{defect_profile['defect_description']}

**Thông tin sản phẩm:**
- Khách hàng: {defect_profile['customer']}
- Mã SP: {defect_profile['part_code']}
- Tên SP: {defect_profile['part_name']}
- Mức độ: {defect_profile['severity']}

**Keywords:** {', '.join(defect_profile['keywords'])}
            """

            await update.message.reply_text(message, parse_mode='Markdown')

            # Send reference image if available
            if defect_profile.get('reference_images'):
                ref_image_url = defect_profile['reference_images'][0]
                try:
                    # Download reference image from backend
                    async with httpx.AsyncClient() as client:
                        ref_response = await client.get(f"{API_BASE_URL}{ref_image_url}")
                        if ref_response.status_code == 200:
                            await update.message.reply_photo(
                                photo=ref_response.content,
                                caption="📷 Ảnh tham khảo"
                            )
                        else:
                            print(f"Failed to download reference image: {ref_response.status_code}")
                except Exception as e:
                    print(f"Error sending reference image: {e}")

        elif response.status_code == 404:
            await update.message.reply_text(
                "❌ Không tìm thấy lỗi phù hợp.\n\n"
                "Độ tin cậy quá thấp. Vui lòng:\n"
                "- Chụp ảnh rõ hơn\n"
                "- Đảm bảo ánh sáng đủ\n"
                "- Hoặc liên hệ QC team để thêm loại lỗi mới"
            )
        else:
            await update.message.reply_text(
                f"❌ Lỗi API: {response.status_code}\n"
                "Vui lòng thử lại sau."
            )

    except httpx.TimeoutException as e:
        print(f"❌ [TIMEOUT ERROR] {e}")
        await update.message.reply_text(
            "⏱ Timeout: Xử lý ảnh quá lâu. Vui lòng thử lại."
        )
    except Exception as e:
        print(f"❌ [GENERAL ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            "❌ Có lỗi xảy ra khi xử lý ảnh.\n"
            "Vui lòng thử lại hoặc liên hệ admin."
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    print(f"💬 [DEBUG] handle_text called! Message: {update.message.text[:50] if update.message.text else 'N/A'}")
    await update.message.reply_text(
        "📸 Vui lòng gửi **ảnh** lỗi sản phẩm để tôi phân tích.\n\n"
        "Sử dụng /help để xem hướng dẫn.",
        parse_mode='Markdown'
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    print(f"❌ [ERROR] {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Đã xảy ra lỗi. Vui lòng thử lại hoặc liên hệ admin."
        )


def main():
    """Run the bot"""
    print("Starting Telegram Bot...")
    print(f"API Base URL: {API_BASE_URL}")

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start bot
    print("Bot is running... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
