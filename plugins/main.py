from pyrogram import Client, filters
from api import grapeapi
from api import command, modules_actions, module
import psutil, platform, os, subprocess, requests


def b2mb(b):
    return round(b / 1024 / 1024, 1)


@Client.on_message(filters.command("bot", prefixes=grapeapi.prefix.get_prefix()) & filters.me)
async def bot_info(client, message):
    termux_execution = "PREFIX" in os.environ
    if termux_execution:
        android_version_process = subprocess.run(['getprop', 'ro.build.version.release'], capture_output=True,
                                                 text=True)
        android_version = android_version_process.stdout.strip()
        system = f"Termux [android {android_version}]"
    else:
        system = platform.system()

    me = await client.get_me()

    text = f"""
🍇 GrapeUserBot

<pre>
 | Owner: {me.mention}
 | Version: {float(open("files/version.txt", "r").read())} BETA TEST
 | System: {system} 
 | RAM: {b2mb(psutil.virtual_memory().total - psutil.virtual_memory().available)} / {b2mb(psutil.virtual_memory().total)} ({psutil.virtual_memory().percent}%)
 | Prefix: {grapeapi.prefix.get_prefix()}
 | Userbot by fimkov
</pre>
"""

    try:
        await message.reply_photo(photo="logo.jpg", caption=text)
        await message.delete()
    except Exception as e:
        print(e)
        await message.edit(text=text, disable_web_page_preview=True)


@Client.on_message(filters.command("help", prefixes=grapeapi.prefix.get_prefix()) & filters.me)
async def modules_helper(_, message):
    try:
        module_for_get = message.command[1]
    except:
        module_for_get = None

    if module_for_get:
        module_target = modules_actions.get_module(module_for_get)
        if not module_target:
            await message.edit(
                text="Module not found",
                disable_web_page_preview=True
            )
            return

        commands = module_target.get_commands()
        commands_formated = ""
        for command in commands:
            commands_formated = commands_formated + f"<code>{grapeapi.prefix.get_prefix()}{command.command}</code> - <i>{command.desc}</i>\n"

        await message.edit(f"""
🍇 Module: <code>{module_target.name}</code>
🛠️ Version: <code>{module_target.version}</code>
📃 Desc: <code>{module_target.desc}</code>

❓ Commands:
{commands_formated}
        """)
    else:
        modules = modules_actions.get_modules()
        modules_formated = ""
        for module in modules:
            modules_formated += f"<code>{module.name}</code>\n"

        await message.edit(f"""
🍇 GrapeUserBot modules:
{modules_formated}

❓ Total modules: <code>{len(modules)}</code>
❓ Get info about module: <code>{grapeapi.prefix.get_prefix()}help [module_name]</code>
        """)


@Client.on_message(filters.command('lm', prefixes=grapeapi.prefix.get_prefix()) & filters.me)
async def load_module(client, message):
    try:
        module_for_load = message.command[1]
    except:
        module_for_load = None

    if module_for_load:
        if not module_for_load.startswith("https://" or "http://"):
            module_for_load = "https://raw.githubusercontent.com/fimkov/GrapeUserBotModules/main/" + module_for_load + ".py"

        if "raw.githubusercontent.com" not in module_for_load:
            await message.edit("<b>only github support</b>")
            return

        await message.edit("<b>getting module...</b>")
        try:
            request_module = requests.get(module_for_load, timeout=10)
        except requests.exceptions.Timeout:
            await message.edit("<b>timeout error</b>")
            return

        except requests.exceptions.ConnectionError:
            await message.edit("<b>connection error</b>")
            return

        await message.edit("<b>loading module...</b>")
        try:
            with open('plugins/' + module_for_load.split('/')[-1], 'w+') as file:
                file.write(request_module.text)
                file.close()
        except:
            await message.edit("<b>error loading module</b>")
            return

        await message.edit("<b>loaded. rebooting...</b>")
        await grapeapi.restart(message)
    else:
        if not message.reply_to_message:
            await message.edit("<b>reply to a message or paste link // name of module</b>")
            return

        await message.edit("<b>loading module...</b>")

        try:
            await client.download_media(message.reply_to_message.document, file_name='plugins/')
        except:
            await message.edit("<b>error loading module</b>")
            return

        await message.edit("<b>loaded. rebooting...</b>")
        await grapeapi.restart(message)


@Client.on_message(filters.command("um", prefixes=grapeapi.prefix.get_prefix()) & filters.me)
async def upload_module(client, message):
    try:
        module_for_upload = message.command[1]
    except:
        await message.edit("<b>need module name</b>")
        return

    if modules_actions.get_module(module_for_upload):
        module_file = modules_actions.get_module(module_for_upload)
    else:
        await message.edit("<b>module not found</b>")
        return

    try:
        caption = """
🍇 Module: <code>{}</code>
🛠️ Version: <code>{}</code>
📃 Desc: <code>{}</code>

❓ Commands:
{}
        """
        commands = module_file.get_commands()
        commands_formated = ""
        for command in commands:
            commands_formated = commands_formated + f"<code>{grapeapi.prefix.get_prefix()}{command.command}</code> - <i>{command.desc}</i>\n"

        await message.delete()
        await client.send_document(chat_id=message.chat.id, document=module_file.file,
                                   caption=caption.format(module_file.name, module_file.version, module_file.desc,
                                                          commands_formated))

    except Exception as e:
        await message.edit("<b>sending module error</b>")
        print(e)


@Client.on_message(filters.command("rm", grapeapi.prefix.get_prefix()) & filters.me)
async def remove_module(client, message):
    try:
        module_for_remove = message.command[1]
    except:
        await message.edit("<b>module name not found</b>")
        return

    if not modules_actions.get_module(module_for_remove):
        await message.edit("<b>module not found</b>")
        return

    os.remove(modules_actions.get_module(module_for_remove).file)
    await message.edit("successfully removed. rebooting...")
    await grapeapi.restart(message)

base_module = module("base", "base of GrapeUserBot", str(__file__), 1.0, [
    command("bot", "get info about bot"),
    command("help", "get info about commands or command"),
    command("lm", "load module by link or name or reply to file"),
    command("um", "like argument get module name. upload module to chat"),
    command("rm", "like argument get module name. remove module")
])

modules_actions.add_module(base_module)
