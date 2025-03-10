from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
import json
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = 'YOUR_BOT_TOKEN'

# Directory to store group data files
DATA_DIR = 'group_data'

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def get_data_file(chat_id: int) -> str:
    """Get the path to the data file for a specific chat."""
    return os.path.join(DATA_DIR, f"{chat_id}_data.json")

def load_data(chat_id: int) -> dict:
    """Load group data from the JSON file for a specific chat."""
    data_file = get_data_file(chat_id)
    try:
        if os.path.exists(data_file):
            with open(data_file, 'r') as file:
                # Check if the file is empty
                if os.path.getsize(data_file) == 0:
                    logger.warning(f"{data_file} is empty. Initializing with an empty dictionary.")
                    return {}
                # Load the JSON data
                data = json.load(file)
                logger.info(f"Loaded data from {data_file}: {data}")
                return data
        else:
            logger.info(f"{data_file} does not exist. Creating a new file.")
            # Create the file and initialize it with an empty dictionary
            with open(data_file, 'w') as file:
                json.dump({}, file)
            return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {data_file}: {e}")
        # If the file contains invalid JSON, reset it to an empty dictionary
        with open(data_file, 'w') as file:
            json.dump({}, file)
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading {data_file}: {e}")
        return {}

def save_data(chat_id: int, data: dict) -> None:
    """Save group data to the JSON file for a specific chat."""
    data_file = get_data_file(chat_id)
    try:
        with open(data_file, 'w') as file:
            json.dump(data, file, indent=4)
            logger.info(f"Saved data to {data_file}: {data}")
    except Exception as e:
        logger.error(f"Error saving data to {data_file}: {e}")

async def creategroup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /creategroup command."""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    # Check if the command has the correct number of arguments
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /creategroup <groupname>")
        return

    group_name = context.args[0]

    # Load data for this chat
    groups = load_data(chat_id)

    # Check if the group already exists
    if group_name in groups:
        await update.message.reply_text(f"Group '{group_name}' already exists!")
        return

    # Create the group and add the creator as the first member
    groups[group_name] = [update.message.from_user.username]
    save_data(chat_id, groups)  # Save the updated data
    await update.message.reply_text(f"Group '{group_name}' created successfully!")

async def tag(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /tag command."""
    chat_id = update.message.chat_id

    # Check if the command has the correct number of arguments
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /tag <groupname>")
        return

    group_name = context.args[0]

    # Load data for this chat
    groups = load_data(chat_id)

    # Check if the group exists
    if group_name not in groups:
        await update.message.reply_text(f"Group '{group_name}' does not exist!")
        return

    # Get the usernames in the group
    usernames = [f"@{username}" for username in groups[group_name]]

    # Tag everyone in the group
    if usernames:
        await update.message.reply_text(' '.join(usernames))
    else:
        await update.message.reply_text(f"No members found in group '{group_name}'.")

async def addtogroup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /addtogroup command."""
    chat_id = update.message.chat_id

    # Check if the command has the correct number of arguments
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addtogroup <groupname> <username>")
        return

    group_name = context.args[0]
    username = context.args[1].lstrip('@')  # Remove '@' if present

    # Load data for this chat
    groups = load_data(chat_id)

    # Check if the group exists
    if group_name not in groups:
        await update.message.reply_text(f"Group '{group_name}' does not exist!")
        return

    # Add the user to the group
    if username not in groups[group_name]:
        groups[group_name].append(username)
        save_data(chat_id, groups)  # Save the updated data
        await update.message.reply_text(f"@{username} added to group '{group_name}'!")
    else:
        await update.message.reply_text(f"@{username} is already in group '{group_name}'.")

async def deletefromgroup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /deletefromgroup command."""
    chat_id = update.message.chat_id

    # Check if the command has the correct number of arguments
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /deletefromgroup <groupname> <username>")
        return

    group_name = context.args[0]
    username = context.args[1].lstrip('@')  # Remove '@' if present

    # Load data for this chat
    groups = load_data(chat_id)

    # Check if the group exists
    if group_name not in groups:
        await update.message.reply_text(f"Group '{group_name}' does not exist!")
        return

    # Check if the user is in the group
    if username in groups[group_name]:
        groups[group_name].remove(username)
        save_data(chat_id, groups)  # Save the updated data
        await update.message.reply_text(f"@{username} removed from group '{group_name}'!")
    else:
        await update.message.reply_text(f"@{username} is not in group '{group_name}'.")

async def deletegroup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /deletegroup command."""
    chat_id = update.message.chat_id

    # Check if the command has the correct number of arguments
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /deletegroup <groupname>")
        return

    group_name = context.args[0]

    # Load data for this chat
    groups = load_data(chat_id)

    # Check if the group exists
    if group_name not in groups:
        await update.message.reply_text(f"Group '{group_name}' does not exist!")
        return

    # Delete the group
    del groups[group_name]
    save_data(chat_id, groups)  # Save the updated data
    await update.message.reply_text(f"Group '{group_name}' deleted successfully!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /help command."""
    help_text = """
🤖 **Bot Commands:**

1. `/creategroup <groupname>` - Create a new group.
2. `/tag <groupname>` - Tag all members in a group.
3. `/addtogroup <groupname> <username>` - Add a user to a group.
4. `/deletefromgroup <groupname> <username>` - Remove a user from a group.
5. `/deletegroup <groupname>` - Delete a group.
6. `/help` - Show this help message.

📝 **Examples:**
- `/creategroup mygroup`
- `/tag mygroup`
- `/addtogroup mygroup @username`
- `/deletefromgroup mygroup @username`
- `/deletegroup mygroup`
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Register the /creategroup command
    application.add_handler(CommandHandler("creategroup", creategroup))

    # Register the /tag command
    application.add_handler(CommandHandler("tag", tag))

    # Register the /addtogroup command
    application.add_handler(CommandHandler("addtogroup", addtogroup))

    # Register the /deletefromgroup command
    application.add_handler(CommandHandler("deletefromgroup", deletefromgroup))

    # Register the /deletegroup command
    application.add_handler(CommandHandler("deletegroup", deletegroup))

    # Register the /help command
    application.add_handler(CommandHandler("help", help_command))

    # Add inline hints (autocomplete suggestions)
    commands = [
        ("creategroup", "Create a new group"),
        ("tag", "Tag all members in a group"),
        ("addtogroup", "Add a user to a group"),
        ("deletefromgroup", "Remove a user from a group"),
        ("deletegroup", "Delete a group"),
        ("help", "Show help message"),
    ]
    application.bot.set_my_commands(commands)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
