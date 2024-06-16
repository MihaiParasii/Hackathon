import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, Updater, ConversationHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from price_api import get_prices, authentificate, select_preferences
from dtos import UserPreferences
from proxy_api import getCategories, getBrandsByCategory

user_selections = {}

MENU, OPTION1, OPTION2 = range(3)

#telegram bot
Telegram_Bot_Token = "6618778005:AAGT5y4T1SJMMKRtukiYueH4Fa25M6ZVee4"


# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Define a function to start the conversation
def main():
    # Initialize the Application with your bot token
    app = Application.builder().token(Telegram_Bot_Token).build()

    authentificate()

    # Register command handlers
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("top", get_greatest_sale))

    app.add_handler(CommandHandler("filter", filter))
    categories = getCategories()
    pattern = "^(" + "|".join(categories) + ")$"
    app.add_handler(CallbackQueryHandler(poll_answer, pattern=pattern))

    app.add_handler(CommandHandler("phone", filter_phones))
    brands = sorted(getBrandsByCategory("PHONE"))
    brands = [s for s in brands if s != ""]
    pattern_brands = "^(" + "|".join(brands) + ")$"
    app.add_handler(CallbackQueryHandler(poll_answer_phones, pattern=pattern_brands))
    
    # app.add_handler(CallbackQueryHandler(select_brands, pattern=r'^select_brand_.*$'))

    # Register a message handler
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command), 0)

    # Start the bot
    app.run_polling()

async def help(update, context):
    await update.message.reply_text("/top - top 5 discounts\n/filter - select preferences")

# Define a function to handle the /get_greatest_sale command
async def get_greatest_sale(update, context):
    # Implement logic to fetch the greatest sale and respond
    user = update.message.from_user
  
    prices = get_prices(user)
    if prices != None:
        for item in prices:
            await update.message.reply_text(f"Discount: {item['disc']}%\n{item['link']}")
    else:
        await update.message.reply_text(f"Can't fetch")


# Define a function to handle incoming messages
async def echo(update, context):
    await update.message.reply_text(update.message.text)

async def unknown_command(update, context):
    await update.message.reply_text(f'Sorry, I didn\'t understand that command.')

async def filter(update: Update, context):
    # Create a list of poll options as InlineKeyboardButtons
    poll_options = getCategories()
    print(poll_options)
    poll_options_buttons = [InlineKeyboardButton(option, callback_data=option) for option in poll_options]

    # Create an InlineKeyboardMarkup to display the poll options
    reply_markup = InlineKeyboardMarkup([poll_options_buttons])
    poll_question = "Select the product category:"
    # Send the poll question with options
    await update.message.reply_text(poll_question, reply_markup=reply_markup)


async def filter_phones(update: Update, context):
    # Create a list of poll options as InlineKeyboardButtons
    category = "PHONE"
    
    brands = sorted(getBrandsByCategory("PHONE"))
    brands = [s for s in brands if s != ""]
    poll_options = brands
    print(poll_options)

    poll_options_buttons = [InlineKeyboardButton(option, callback_data=option) for option in poll_options]
    keyboard = [poll_options_buttons[i:i+2] for i in range(0, len(poll_options_buttons), 2)]
    print("keyboard")
    print(keyboard)

    # Create an InlineKeyboardMarkup to display the poll options
    reply_markup = InlineKeyboardMarkup(keyboard)
    poll_question = "Select the "+ category + " brand: "
    print()
    print(poll_question)
    # Send the poll question with options
    await update.message.reply_text(poll_question, reply_markup=reply_markup)


async def poll_answer(update: Update, context):
    query = update.callback_query
    user = query.from_user
    option = query.data
    print("option: ")
    print(option)

    # Toggle the user's selection
    if user.id in user_selections:
        if option in user_selections[user.id]:
            user_selections[user.id].remove(option)
        else:
            user_selections[user.id].append(option)
    else:
        user_selections[user.id] = [option]

    # Update the message to reflect the user's selections
    selected_option_text = ", ".join(user_selections[user.id])
    await query.edit_message_text(
        text=f"You selected: {selected_option_text}",
        reply_markup=create_selection_markup(user.id),
    )

def create_selection_markup(user_id):
    selected_options = user_selections.get(user_id, [])
    poll_options_buttons = []
    poll_options = getCategories()
    print(poll_options)
    for option in poll_options:
        if option in selected_options:
            button = InlineKeyboardButton(f"✅ {option}", callback_data=option)
        else:
            button = InlineKeyboardButton(f"❌ {option}", callback_data=option)
        poll_options_buttons.append(button)
    
    categories = [x for x in poll_options if x in selected_options]
    user_prefe = UserPreferences(user_id)
    user_prefe.categories = categories
    select_preferences(user_prefe)
    return InlineKeyboardMarkup([poll_options_buttons])



# BRANDS
async def poll_answer_phones(update: Update, context):
    query = update.callback_query
    user = query.from_user
    option = query.data
    print("option: ")
    print(option)

    # Toggle the user's selection
    if user.id in user_selections:
        if option in user_selections[user.id]:
            user_selections[user.id].remove(option)
        else:
            user_selections[user.id].append(option)
    else:
        user_selections[user.id] = [option]

    # Update the message to reflect the user's selections
    selected_option_text = ", ".join(user_selections[user.id])
    await query.edit_message_text(
        text=f"You selected: {selected_option_text}",
        reply_markup=create_selection_markup_phones(user.id),
    )

def create_selection_markup_phones(user_id):
    selected_options = user_selections.get(user_id, [])
    poll_options_buttons = []
    brands = sorted(getBrandsByCategory("PHONE"))
    brands = [s for s in brands if s != ""]
    poll_options = brands
    for option in poll_options:
        if option in selected_options:
            button = InlineKeyboardButton(f"✅ {option}", callback_data=option)
        else:
            button = InlineKeyboardButton(f"❌ {option}", callback_data=option)
        poll_options_buttons.append(button)
    keyboard = [poll_options_buttons[i:i+2] for i in range(0, len(poll_options_buttons), 2)]
    
    brands = [x for x in poll_options if x in selected_options]
    user_prefe = UserPreferences(user_id)
    user_prefe.brands = brands
    print("selected brands = ")
    print(brands)
    # select_preferences(user_prefe)
    return InlineKeyboardMarkup(keyboard)


def getAllBrandsByCategory(category):
    return getBrandsByCategory(category)



async def select_brands(update: Update, context):
    query = update.callback_query
    user = query.from_user
    data = query.data.split('_')
    category_index = int(data[2])
    category = getCategories()[category_index]


    # Retrieve brands for the selected category
    brands = getAllBrandsByCategory(category)
    print("BRANDS")
    print(brands)

    # Create a list of poll options for brands as InlineKeyboardButtons
    brand_options_buttons = [InlineKeyboardButton(brand, callback_data=f'select_brand_{brand}') for brand in brands]

    # Create an InlineKeyboardMarkup to display the brand options
    reply_markup = InlineKeyboardMarkup([brand_options_buttons])
    
    # Send the brand options to the user
    await query.message.reply_text(f"Select a brand for the category '{category}':", reply_markup=reply_markup)


if __name__ == '__main__':
    main()
