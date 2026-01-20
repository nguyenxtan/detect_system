"""Telegram Bot for defect reporting"""
import os
import sys
import asyncio
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
from context_storage import (
    get_user_context,
    set_user_customer,
    set_user_product,
    clear_user_context,
    get_context_summary
)

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
/set_customer - Chọn khách hàng
/set_product - Chọn sản phẩm
/context - Xem context hiện tại
/report - Báo cáo lỗi
/history - Xem lịch sử 10 báo cáo gần nhất
/help - Hướng dẫn sử dụng

**Cách sử dụng:**
1. Thiết lập context: /set_customer → /set_product
2. Gửi ảnh lỗi sản phẩm
3. Bot phân tích và trả về kết quả

Dùng /set_customer để bắt đầu! 🚀
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


async def context_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /context command - show current context"""
    user_id = str(update.effective_user.id)
    summary = get_context_summary(user_id)
    await update.message.reply_text(summary, parse_mode='Markdown')


async def set_customer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /set_customer command - show customer list"""
    await update.message.reply_text("🔄 Đang tải danh sách khách hàng...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/customers")

        if response.status_code == 200:
            customers = response.json()

            if not customers:
                await update.message.reply_text("❌ Không có khách hàng nào trong hệ thống.")
                return

            # Create inline keyboard with customer buttons
            keyboard = []
            for customer in customers:
                keyboard.append([
                    InlineKeyboardButton(
                        text=customer['customer_name'],
                        callback_data=f"customer_{customer['id']}_{customer['customer_name']}"
                    )
                ])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "👥 **Chọn khách hàng:**",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(f"❌ Lỗi API: {response.status_code}")

    except Exception as e:
        print(f"Error fetching customers: {e}")
        await update.message.reply_text("❌ Không thể tải danh sách khách hàng. Vui lòng thử lại.")


async def set_product_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /set_product command - show product list filtered by customer"""
    user_id = str(update.effective_user.id)
    user_context = get_user_context(user_id)

    if not user_context or not user_context.get('customer_id'):
        await update.message.reply_text(
            "❌ Vui lòng chọn khách hàng trước bằng lệnh /set_customer"
        )
        return

    await update.message.reply_text("🔄 Đang tải danh sách sản phẩm...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/products")

        if response.status_code == 200:
            all_products = response.json()
            # Filter products by customer_id
            customer_id = user_context['customer_id']
            products = [p for p in all_products if p['customer_id'] == customer_id]

            if not products:
                await update.message.reply_text(
                    f"❌ Không có sản phẩm nào cho khách hàng {user_context['customer_name']}."
                )
                return

            # Create inline keyboard with product buttons
            keyboard = []
            for product in products:
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"{product['product_code']} - {product['product_name']}",
                        callback_data=f"product_{product['id']}_{product['product_code']}_{product['product_name']}"
                    )
                ])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"📦 **Chọn sản phẩm của {user_context['customer_name']}:**",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(f"❌ Lỗi API: {response.status_code}")

    except Exception as e:
        print(f"Error fetching products: {e}")
        await update.message.reply_text("❌ Không thể tải danh sách sản phẩm. Vui lòng thử lại.")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button callbacks"""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    data = query.data

    if data.startswith("customer_"):
        # Format: customer_{id}_{name}
        parts = data.split("_", 2)
        customer_id = int(parts[1])
        customer_name = parts[2]

        set_user_customer(user_id, customer_id, customer_name)

        await query.edit_message_text(
            f"✅ Đã chọn khách hàng: **{customer_name}**\n\n"
            f"Tiếp theo, dùng /set_product để chọn sản phẩm.",
            parse_mode='Markdown'
        )

    elif data.startswith("product_"):
        # Format: product_{id}_{code}_{name}
        parts = data.split("_", 3)
        product_id = int(parts[1])
        product_code = parts[2]
        product_name = parts[3]

        try:
            set_user_product(user_id, product_id, product_name, product_code)

            user_context = get_user_context(user_id)
            await query.edit_message_text(
                f"✅ Đã thiết lập context:\n\n"
                f"🏢 Khách hàng: **{user_context['customer_name']}**\n"
                f"📦 Sản phẩm: **{product_code} - {product_name}**\n\n"
                f"Bây giờ bạn có thể gửi ảnh để phân tích! 📸",
                parse_mode='Markdown'
            )
        except ValueError as e:
            await query.edit_message_text(f"❌ {str(e)}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages"""
    user_id = str(update.effective_user.id)
    print(f"📸 [DEBUG] handle_photo called! User: {user_id}")

    # Check if context is set
    user_context = get_user_context(user_id)

    if not user_context or not user_context.get('customer_id') or not user_context.get('product_id'):
        await update.message.reply_text(
            "❌ **Vui lòng thiết lập context trước:**\n\n"
            "1️⃣ /set_customer - Chọn khách hàng\n"
            "2️⃣ /set_product - Chọn sản phẩm\n\n"
            "Sau đó gửi lại ảnh để phân tích.",
            parse_mode='Markdown'
        )
        return

    await update.message.reply_text(
        f"🔍 Đang phân tích ảnh cho:\n"
        f"🏢 {user_context['customer_name']}\n"
        f"📦 {user_context['product_code']} - {user_context['product_name']}\n\n"
        f"Vui lòng đợi..."
    )

    try:
        # Get the largest photo
        photo = update.message.photo[-1]
        photo_file = await photo.get_file()

        # Download photo
        photo_bytes = await photo_file.download_as_bytearray()

        # Send to API for matching with context
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
            data = {
                "user_id": user_id,
                "customer_id": str(user_context['customer_id']),
                "product_id": str(user_context['product_id'])
            }
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
    application.add_handler(CommandHandler("context", context_command))
    application.add_handler(CommandHandler("set_customer", set_customer_command))
    application.add_handler(CommandHandler("set_product", set_product_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start bot
    print("Bot is running... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
