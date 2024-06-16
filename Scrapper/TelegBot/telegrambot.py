import logging
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.constants import ParseMode

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your Flask API base URL
API_BASE_URL = 'http://localhost:5000'

# Replace with your Telegram bot token
TELEGRAM_BOT_TOKEN = '6618778005:AAGT5y4T1SJMMKRtukiYueH4Fa25M6ZVee4'

# This token will be used for authenticating API requests
API_TOKEN = "3IyVavY0NHtC6HePbs_PoA"

# Start command with buttons
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Categories", callback_data='categories')],
        [InlineKeyboardButton("Preferences", callback_data='preferences')],
        [InlineKeyboardButton("Top Prices MW", callback_data='top_prices_mw')],
        [InlineKeyboardButton("Top Discount Products by Category", callback_data='top_discount_products')],
        [InlineKeyboardButton("Top Discount Products by Brand", callback_data='top_discount_products_brand')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Hi! Choose an option:', reply_markup=reply_markup)

# Inline button handler
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # Answer the callback query

    if query.data == 'categories':
        await categories(query, context)
    elif query.data == 'preferences':
        await preferences(query, context)
    elif query.data == 'top_prices_mw':
        await top_prices_mw(query, context)
    elif query.data == 'top_discount_products':
        await show_categories(query, context)
    elif query.data == 'top_discount_products_brand':
        await show_brands(query, context)

async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('/categories - Get product categories\n'
                                    '/preferences - Get user preferences\n'
                                    '/top_prices_mw - Get top prices from MW\n'
                                    '/top_discount_products <category> - Get top discount products by category\n'
                                    '/top_discount_products_brand <brand> - Get top discount products by brand\n')

async def categories(update: Update, context: CallbackContext) -> None:
    response = requests.get(f'{API_BASE_URL}/filter/categories', headers={'Authorization': f'Bearer {API_TOKEN}'})

    if response.status_code == 200:
        categories = response.json().get('categories', [])
        await update.message.reply_text('Categories:\n' + '\n'.join(categories))
    else:
        await update.message.reply_text('Failed to fetch categories.')

async def preferences(update: Update, context: CallbackContext) -> None:
    response = requests.get(f'{API_BASE_URL}/preferences', headers={'Authorization': f'Bearer {API_TOKEN}'})

    if response.status_code == 200:
        preferences = response.json().get('preferences', [])
        message = 'Preferences:\n' + '\n'.join([f"{p['name']} - {p['category']} - {p['brand']}" for p in preferences])
        await update.message.reply_text(message)
    else:
        await update.message.reply_text('Failed to fetch preferences.')

async def top_prices_mw(update: Update, context: CallbackContext) -> None:
    response = requests.get(f'{API_BASE_URL}/top_prices_mw', headers={'Authorization': f'Bearer {API_TOKEN}'})

    if response.status_code == 200:
        top_prices = response.json().get('top_prices_mw', [])
        message = 'Top Prices MW:\n' + '\n'.join([f"{p['name']} - {p['price']} - {p['discount']} - {p['link']}" for p in top_prices])
        await update.message.reply_text(message)
    else:
        await update.message.reply_text('Failed to fetch top prices from MW.')

async def show_categories(query, context: CallbackContext) -> None:
    response = requests.get(f'{API_BASE_URL}/filter/categories', headers={'Authorization': f'Bearer {API_TOKEN}'})

    if response.status_code == 200:
        categories = response.json().get('categories', [])
        keyboard = [
            [InlineKeyboardButton(category, callback_data=f'/top_discount_products_category {category}')]
            for category in categories
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text('Choose a category:', reply_markup=reply_markup)
    else:
        await query.message.reply_text('Failed to fetch categories.')

async def show_brands(query, context: CallbackContext) -> None:
    response = requests.get(f'{API_BASE_URL}/filter/brands', headers={'Authorization': f'Bearer {API_TOKEN}'})

    if response.status_code == 200:
        brands = response.json().get('brands', [])
        keyboard = [
            [InlineKeyboardButton(brand, callback_data=f'/top_discount_products_brand {brand}')]
            for brand in brands
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text('Choose a brand:', reply_markup=reply_markup)
    else:
        await query.message.reply_text('Failed to fetch brands.')

# async def top_discount_products(update: Update, context: CallbackContext) -> None:
#     query_data = update.callback_query.data
#     if query_data.startswith('top_discount_products_category_'):
#         category = query_data.split(' ')[-1]
#         response = requests.get(
#             f'{API_BASE_URL}/top_discount_products/{category}',
#             headers={'Authorization': f'Bearer {API_TOKEN}'}
#         )
#     elif query_data.startswith('top_discount_products_brand_'):
#         brand = query_data.split('_')[-1]
#         response = requests.get(
#             f'{API_BASE_URL}/top_discount_products/brand/{brand}',
#             headers={'Authorization': f'Bearer {API_TOKEN}'}
#         )
#     else:
#         await update.callback_query.message.reply_text('Invalid selection')
#         return
#
#     if response.status_code == 200:
#         products = response.json().get('top_discount_products', [])
#         message = 'Top Discount Products:\n' + '\n'.join(
#             [f"{p['name']} - {p['discount']} - {p['category']} - {p['link']}" for p in products]
#         )
#         await update.callback_query.message.reply_text(message)
#     else:
#         await update.callback_query.message.reply_text('Failed to fetch top discount products.')


# async def top_discount_products(update: Update, context: CallbackContext) -> None:
#     category = update.callback_query.data.split('_')[-1]
#     print(category)
#     print(update.callback_query.data)
#     response = requests.get(f'{API_BASE_URL}/top_discount_products/{category}', headers={'Authorization': f'Bearer {API_TOKEN}'})
#
#     if response.status_code == 200:
#         products = response.json().get('top_discount_products', [])
#         message = 'Top Discount Products:\n' + '\n'.join([f"{p['name']} - {p['discount']} - {p['category']} - {p['link']}" for p in products])
#         await update.callback_query.message.reply_text(message)
#     else:
#         await update.callback_query.message.reply_text('Failed to fetch top discount products.')
#
# async def top_discount_products_brand(update: Update, context: CallbackContext) -> None:
#     brand = update.callback_query.data.split('_')[-1]
#     response = requests.get(f'{API_BASE_URL}/top_discount_products/brand/{brand}', headers={'Authorization': f'Bearer {API_TOKEN}'})
#
#     if response.status_code == 200:
#         products = response.json().get('top_discount_products', [])
#         message = 'Top Discount Products:\n' + '\n'.join([f"{p['name']} - {p['discount']} - {p['category']} - {p['link']}" for p in products])
#         await update.callback_query.message.reply_text(message)
#     else:
#         await update.callback_query.message.reply_text('Failed to fetch top discount products.')



async def top_discount_products(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        await update.message.reply_text('Usage: /top_discount_products <category>')
        return

    category = context.args[0]

    response = requests.get(f'{API_BASE_URL}/top_discount_products/{category}', headers={'Authorization': f'Bearer {API_TOKEN}'})

    if response.status_code == 200:
        products = response.json().get('top_discount_products', [])
        message = 'Top Discount Products:\n' + '\n'.join([f"{p['name']} - {p['discount']} - {p['category']} - {p['link']}" for p in products])
        await update.message.reply_text(message)
    else:
        await update.message.reply_text('Failed to fetch top discount products.')

async def top_discount_products_brand(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        await update.message.reply_text('Usage: /top_discount_products_brand <brand>')
        return

    brand = context.args[0]
    response = requests.get(f'{API_BASE_URL}/top_discount_products/brand/{brand}', headers={'Authorization': f'Bearer {API_TOKEN}'})

    if response.status_code == 200:
        products = response.json().get('top_discount_products', [])
        message = 'Top Discount Products:\n' + '\n'.join([f"{p['name']} - {p['discount']} - {p['category']} - {p['link']}" for p in products])
        await update.message.reply_text(message)
    else:
        await update.message.reply_text('Failed to fetch top discount products.')

def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("categories", categories))
    application.add_handler(CommandHandler("preferences", preferences))
    application.add_handler(CommandHandler("top_prices_mw", top_prices_mw))
    application.add_handler(CommandHandler("top_discount_products", top_discount_products))
    application.add_handler(CommandHandler("top_discount_products_brand", top_discount_products_brand))

    application.run_polling()

if __name__ == '__main__':
    main()
