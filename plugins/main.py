from pyrogram import Client, filters
from api import grapeapi
import psutil, platform, os, subprocess, asyncio


def b2mb(b):
    return round(b / 1024 / 1024, 1)


@Client.on_message(filters.command("bot") & filters.me)
async def bot_info(client, message):
    termux_execution = "PREFIX" in os.environ
    if termux_execution:
        android_version_process = subprocess.run(['getprop', 'ro.build.version.release'], capture_output=True,
                                                 text=True)
        android_version = android_version_process.stdout.strip()
        system = f"Termux [Android {android_version}]"
    else:
        system = platform.system()

    me = await client.get_me()

    text = f"""
🍇 GrapeUserBot

<pre>
 | Owner: {me.mention}
 | Version: {float(open("version.txt", "r").read())} BETA TEST
 | System: {system} 
 | RAM: {b2mb(psutil.virtual_memory().total - psutil.virtual_memory().available)} / {b2mb(psutil.virtual_memory().total)} ({psutil.virtual_memory().percent}%)
 | Prefix: {await grapeapi.prefix.get_prefix()}
 | Userbot by fimkov
</pre>
"""

    try:
        await message.reply_photo(photo="logo.jpg", caption=text)
        await message.delete()
    except Exception as e:
        print(e)
        await message.edit(text=text, disable_web_page_preview=True)
