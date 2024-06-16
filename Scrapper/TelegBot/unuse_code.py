async def get_phones(update: Update, context: CallbackContext):
    print("get's here")
    user = update.effective_user
    custom_keyboard = [["Option 1", "Option 2"]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        f"Hi {user.mention_html()}! Please choose an option:",
        reply_markup=reply_markup,
    )

    return MENU


async def select_option(update: Update, context: CallbackContext):
    user = update.effective_user
    selected_option = update.message.text

    if selected_option == "Option 1":
        await update.message.reply_text(f"You selected Option 1")
        return OPTION1
    elif selected_option == "Option 2":
        await update.message.reply_text(f"You selected Option 2")
        return OPTION2

# Function to end the conversation
async def end_conversation(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_text(f"Goodbye, {user.mention_html()}!")
    return ConversationHandler.END


# def main
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", get_phones)],
        states={
            MENU: [MessageHandler(filters.Regex("^(Option 1|Option 2)$"), select_option)],
            OPTION1: [MessageHandler(filters.Text, end_conversation)],
            OPTION2: [MessageHandler(filters.Text, end_conversation)],
        },
        fallbacks=[],
    )
    app.add_handler(conversation_handler)