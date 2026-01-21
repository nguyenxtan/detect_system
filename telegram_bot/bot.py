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
/ping - Kiểm tra kết nối
/setproduct - Chọn sản phẩm (BẮT BUỘC)
/setcustomer - Chọn khách hàng (tùy chọn, để lọc sản phẩm)
/context - Xem context hiện tại
/history - Xem lịch sử 10 báo cáo gần nhất
/help - Hướng dẫn sử dụng

**Cách sử dụng:**
1. Chọn sản phẩm: /setproduct
2. Gửi ảnh lỗi sản phẩm
3. Bot phân tích và trả về kết quả

Dùng /setproduct để bắt đầu! 📸
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


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ping command - simple health check"""
    await update.message.reply_text("🏓 Pong! Bot đang hoạt động bình thường.")


async def set_customer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /set_customer command - show customer list"""
    await update.message.reply_text("🔄 Đang tải danh sách khách hàng...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/customers/public")

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
    """Handle /set_product command - show product list (optionally filtered by customer)"""
    user_id = str(update.effective_user.id)
    user_context = get_user_context(user_id)

    await update.message.reply_text("🔄 Đang tải danh sách sản phẩm...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/products/public")

        if response.status_code == 200:
            all_products = response.json()

            # Filter by customer if set (for better UX), otherwise show all
            if user_context and user_context.get('customer_id'):
                customer_id = user_context['customer_id']
                products = [p for p in all_products if p['customer_id'] == customer_id]
                header_msg = f"📦 **Chọn sản phẩm của {user_context['customer_name']}:**"
            else:
                # Show all products (or top N to avoid overwhelming)
                products = all_products[:50]  # Limit to 50 for UX
                header_msg = "📦 **Chọn sản phẩm:**\n_Tip: Dùng /setcustomer trước để lọc theo khách hàng_"

            if not products:
                await update.message.reply_text(
                    "❌ Không có sản phẩm nào. Vui lòng liên hệ admin."
                )
                return

            # Create inline keyboard with product buttons (include customer_id in callback)
            keyboard = []
            for product in products:
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"{product['product_code']} - {product['product_name']}",
                        callback_data=f"product_{product['id']}_{product['customer_id']}_{product['product_code']}_{product['product_name']}"
                    )
                ])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                header_msg,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Lỗi API: {response.status_code}\n"
                f"Vui lòng thử lại sau."
            )

    except Exception as e:
        print(f"Error fetching products: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            f"❌ Không thể tải danh sách sản phẩm.\n"
            f"Lỗi: {type(e).__name__}\n"
            f"Vui lòng thử lại hoặc liên hệ admin."
        )


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
            f"Tiếp theo, dùng /setproduct để chọn sản phẩm.",
            parse_mode='Markdown'
        )

    elif data.startswith("product_"):
        # Format: product_{id}_{customer_id}_{code}_{name}
        parts = data.split("_", 4)
        product_id = int(parts[1])
        product_customer_id = int(parts[2])
        product_code = parts[3]
        product_name = parts[4]

        # Get user context to check if customer is already set
        user_context = get_user_context(user_id)

        # Fetch customer name from API if not in context
        customer_name = None
        if user_context and user_context.get('customer_id') == product_customer_id:
            customer_name = user_context.get('customer_name')

        # Set product (customer is optional)
        set_user_product(user_id, product_id, product_name, product_code, product_customer_id, customer_name)

        user_context = get_user_context(user_id)

        # Build confirmation message
        if user_context.get('customer_name'):
            msg = (
                f"✅ Đã thiết lập:\n\n"
                f"🏢 Khách hàng: **{user_context['customer_name']}**\n"
                f"📦 Sản phẩm: **{product_code} - {product_name}**\n\n"
                f"Bây giờ bạn có thể gửi ảnh để phân tích! 📸"
            )
        else:
            msg = (
                f"✅ Đã thiết lập sản phẩm:\n\n"
                f"📦 **{product_code} - {product_name}**\n\n"
                f"Bây giờ bạn có thể gửi ảnh để phân tích! 📸"
            )

        await query.edit_message_text(msg, parse_mode='Markdown')


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages"""
    user_id = str(update.effective_user.id)
    print(f"📸 [DEBUG] handle_photo called! User: {user_id}")

    # Check if product is set (customer is optional)
    user_context = get_user_context(user_id)

    if not user_context or not user_context.get('product_id'):
        await update.message.reply_text(
            "❌ **Vui lòng chọn sản phẩm trước:**\n\n"
            "/setproduct - Chọn sản phẩm\n\n"
            "_Tip: Dùng /setcustomer trước để lọc sản phẩm theo khách hàng_\n\n"
            "Sau đó gửi lại ảnh để phân tích.",
            parse_mode='Markdown'
        )
        return

    # Build analysis message
    if user_context.get('customer_name'):
        analysis_msg = (
            f"🔍 Đang phân tích ảnh cho:\n"
            f"🏢 {user_context['customer_name']}\n"
            f"📦 {user_context['product_code']} - {user_context['product_name']}\n\n"
            f"Vui lòng đợi..."
        )
    else:
        analysis_msg = (
            f"🔍 Đang phân tích ảnh cho:\n"
            f"📦 {user_context['product_code']} - {user_context['product_name']}\n\n"
            f"Vui lòng đợi..."
        )

    await update.message.reply_text(analysis_msg)

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
                "product_id": str(user_context['product_id'])
            }
            # Optionally include customer_id if available (for validation)
            if user_context.get('customer_id'):
                data["customer_id"] = str(user_context['customer_id'])

            print(f"📤 [DEBUG] Sending data: {data}")

            response = await client.post(
                f"{API_BASE_URL}/api/defects/match",
                files=files,
                data=data
            )

        print(f"✅ [DEBUG] Response received: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            defect_profile = result.get('defect_profile')
            confidence = result.get('confidence', 0)
            warning = result.get('warning')

            # Handle case where match is null (low confidence)
            if defect_profile is None:
                warning_text = f"\n\n_Lý do: {warning}_" if warning else ""
                await update.message.reply_text(
                    f"❌ **Không tìm thấy lỗi phù hợp**\n\n"
                    f"Độ tin cậy: {confidence:.0%} (quá thấp)\n\n"
                    f"**Vui lòng:**\n"
                    f"- Chụp ảnh rõ hơn, zoom vào vùng lỗi\n"
                    f"- Đảm bảo ánh sáng đủ\n"
                    f"- Chụp từ góc độ rõ ràng hơn\n"
                    f"- Hoặc liên hệ QC team để thêm loại lỗi mới{warning_text}",
                    parse_mode='Markdown'
                )
                return

            # Normal case: defect found
            defect_type = defect_profile['defect_type'].lower()

            # Format response differently for OK vs Defect
            if defect_type == 'ok' or defect_type == 'normal':
                message = f"""
✅ **KẾT QUẢ: KHÔNG CÓ LỖI (OK)**

**Độ tin cậy:** {confidence:.0%}

**Nhận xét:**
{defect_profile['defect_description']}

**Thông tin sản phẩm:**
- Khách hàng: {defect_profile['customer']}
- Mã SP: {defect_profile['part_code']}
- Tên SP: {defect_profile['part_name']}

Sản phẩm đạt chuẩn QC ✓
                """
            else:
                message = f"""
⚠️ **PHÁT HIỆN LỖI**

**Loại lỗi:** `{defect_profile['defect_type']}`
**Tên lỗi:** {defect_profile['defect_title']}
**Độ tin cậy:** {confidence:.0%}

**Mô tả chuẩn QC:**
{defect_profile['defect_description']}

**Thông tin sản phẩm:**
- Khách hàng: {defect_profile['customer']}
- Mã SP: {defect_profile['part_code']}
- Tên SP: {defect_profile['part_name']}
- Mức độ nghiêm trọng: {defect_profile['severity']}

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
            # Parse error detail to differentiate between missing profiles vs low confidence
            try:
                error_detail = response.json().get('detail', '')
            except:
                error_detail = ''

            # Case A: No defect profiles configured for this product
            if 'No defect profiles configured' in error_detail or 'No defect profiles' in error_detail:
                await update.message.reply_text(
                    "❌ **Chưa có dữ liệu lỗi cho sản phẩm này**\n\n"
                    "Hệ thống chưa được cấu hình defect profiles cho sản phẩm bạn đã chọn.\n\n"
                    "**Vui lòng:**\n"
                    "- Kiểm tra lại sản phẩm đã chọn (/context)\n"
                    "- Hoặc liên hệ QC/Admin để thêm dữ liệu lỗi cho sản phẩm này\n\n"
                    "_Lưu ý: Admin cần tạo defect profiles trên web portal trước._",
                    parse_mode='Markdown'
                )
            # Case B: Profiles exist but confidence too low
            elif 'No confident match found' in error_detail or 'confidence' in error_detail.lower():
                await update.message.reply_text(
                    "❌ **Không tìm thấy lỗi phù hợp**\n\n"
                    "Độ tin cậy quá thấp. Vui lòng:\n"
                    "- Chụp ảnh rõ hơn, zoom vào vùng lỗi\n"
                    "- Đảm bảo ánh sáng đủ\n"
                    "- Chụp từ góc độ rõ ràng hơn\n"
                    "- Hoặc liên hệ QC team để thêm loại lỗi mới vào hệ thống",
                    parse_mode='Markdown'
                )
            # Fallback: Generic 404 error
            else:
                await update.message.reply_text(
                    f"❌ Không tìm thấy kết quả phù hợp.\n\n"
                    f"Chi tiết: {error_detail}\n\n"
                    f"Vui lòng liên hệ admin để được hỗ trợ."
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
    print("=" * 60)
    print("🤖 TELEGRAM BOT STARTING")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Bot Token: {'✅ Set' if TELEGRAM_BOT_TOKEN else '❌ Missing'}")
    print(f"Token Length: {len(TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else 0} characters")
    print("=" * 60)

    # Create application
    print("📡 Creating Telegram application...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    print("✅ Application created successfully")

    # Add handlers
    print("📝 Registering command handlers...")
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("context", context_command))
    application.add_handler(CommandHandler("setcustomer", set_customer_command))
    application.add_handler(CommandHandler("set_customer", set_customer_command))  # Backward compat
    application.add_handler(CommandHandler("setproduct", set_product_command))
    application.add_handler(CommandHandler("set_product", set_product_command))  # Backward compat
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("✅ All handlers registered")

    # Add error handler
    application.add_error_handler(error_handler)

    # Start bot
    print("=" * 60)
    print("✅ BOT IS RUNNING")
    print("Press Ctrl+C to stop.")
    print("=" * 60)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
