from pyrogram import Client, filters
from api import grapeapi
from api import command, modules_actions, module
import psutil, platform, os, subprocess, asyncio

modules_actions_instance = modules_actions()


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
async def modules_helper(client, message):
    try:
        module_for_get = message.command[1]
    except:
        module_for_get = None

    if module_for_get:
        module_target = modules_actions_instance.get_module(module_for_get)
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
        modules = modules_actions_instance.get_modules()
        modules_formated = ""
        for module in modules:
            modules_formated += f"<code>{module.name}</code>\n"

        await message.edit(f"""
🍇 GrapeUserBot modules:
{modules_formated}

❓ Total modules: <code>{len(modules)}</code>
❓ Get info about module: <code>{grapeapi.prefix.get_prefix()}help [module_name]</code>
        """)

base_module = module("base", "base of GrapeUserBot", str(__file__), 1.0, [
    command("bot", "get info about bot"),
    command("help", "get info about commands or command")
])

modules_actions_instance.add_module(base_module)
