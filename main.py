import asyncio
import os.path
import sys, logging

from api import grapeapi


class GrapeUserBot:
    def __init__(self):
        self.client = None
        self.api = {
            "id": None,
            "hash": None
        }
        self.version = float(open("files/version.txt", "r").read())
        self.changelog = "[+] updated api\n[+] connected to website\n[+] modules actions"

    @staticmethod
    async def cc():
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    async def requirements_load(debug: bool = False):
        logging.info("progressbar installing...")

        await grapeapi.import_library("tqdm")
        await GrapeUserBot.cc()
        from tqdm import tqdm

        requirements = [
            "pyrogram",
            "aiosqlite",
            "aiogram==2.25.2",
            "requests",
            "colorama",
            "TgCrypto"
        ]

        for lib in tqdm(requirements, desc="Installing libraries..."):
            await grapeapi.import_library(lib)
        await GrapeUserBot.cc()

    @staticmethod
    def check_update() -> bool:
        import requests
        from colorama import Fore

        logging.info("Checking updates...")
        try:
            get_file = requests.get(f"https://raw.githubusercontent.com/fimkov/GrapeUserBot/main/files/version.txt",
                                    timeout=15)
        except requests.exceptions.ConnectTimeout:
            logging.critical("check update failed")
            return False

        if get_file.status_code == 200:
            if float(get_file.text) > GrapeUserBot().version:
                logging.info("update available")
                return True
            else:
                logging.info("updates not found")
                return False
        else:
            logging.critical("check update failed")
            return False

    @staticmethod
    def update():
        if GrapeUserBot.check_update():
            import requests
            from colorama import Fore
            from tqdm import tqdm

            files = [
                "api.py",
                "main.py",
                "plugins/main.py",
                "files/version.txt"
            ]

            for file in tqdm(files, desc="Updating..."):
                try:
                    get_file = requests.get(f"https://raw.githubusercontent.com/fimkov/GrapeUserBot/main/{file}",
                                            timeout=15)
                except requests.exceptions.ConnectTimeout:
                    logging.critical("update failed")
                    return

                with open(file, "w+", encoding="utf-8") as f:
                    f.write(get_file.text)

            logging.info("updated successfully")

    async def main(self):
        logging.info("starting userbot...")
        import pyrogram
        from colorama import Fore as F

        if os.path.isfile("GrapeUserBot.session-journal"):
            os.remove("GrapeUserBot.session-journal")
            logging.info("Session journal removed")

        if os.path.isfile("files/GrapeUserBot.session"):
            logging.info("session file found")
            self.client = pyrogram.Client("GrapeUserBot", plugins=dict(root="plugins"), workdir="files")
            logging.info("session connected")
        else:
            logging.critical("session file not found")
            self.api["id"] = input(F.WHITE + "Enter your api id: ")
            self.api["hash"] = input(F.WHITE + "Enter your api hash: ")
            self.client = pyrogram.Client(
                name="GrapeUserBot",
                api_hash=self.api["hash"],
                api_id=self.api["id"],
                device_model="POCO F5",
                system_version="ANDROID 14",
                app_version="10.10.1",
                lang_code="en",
                plugins=dict(root="plugins"),
                parse_mode=pyrogram.enums.ParseMode.HTML,
                workdir="files"
            )
            logging.info("session created")

        logging.info("running session...")
        await self.client.start()
        logging.info("session started")
        await self.cc()
        if os.path.isfile("restart.txt"):
            f = open("restart.txt", "r")
            chat_id = f.read()
            f.close()

            os.remove("restart.txt")

            try:
                await self.client.send_message(chat_id, "<b>GrapeUserBot successfully rebooted</b>")
            except Exception as e:
                await self.client.send_message("me",
                                                   f"<b>GrapeUserBot rebooted successfully, but an error occurred while "
                                                   f"sending a message\n\nLOG:</b> {e}")
            logging.info("restart message sended")

        print(F.MAGENTA + "   ____                      _   _               ____        _   ")
        print(F.LIGHTCYAN_EX + "  / ___|_ __ __ _ _ __   ___| | | |___  ___ _ __| __ )  ___ | |_ ")
        print(F.MAGENTA + "  / ___|_ __ __ _ _ __   ___| | | |___  ___ _ __| __ )  ___ | |_ ")
        print(F.LIGHTCYAN_EX + " | |  _| '__/ _` | '_ \ / _ \ | | / __|/ _ \ '__|  _ \ / _ \| __|")
        print(F.MAGENTA + " | |_| | | | (_| | |_) |  __/ |_| \__ \  __/ |  | |_) | (_) | |_ ")
        print(F.LIGHTCYAN_EX + "  \____|_|  \__,_| .__/ \___|\___/|___/\___|_|  |____/ \___/ \__|")
        print(F.MAGENTA + "                 |_|")
        print("")
        print(F.LIGHTCYAN_EX + f"for get modules - {grapeapi.prefix.get_prefix()}help")
        print(F.MAGENTA + f"for get bot info - {grapeapi.prefix.get_prefix()}bot")
        print("")
        print(F.LIGHTCYAN_EX + "version: " + str(self.version) + "\n")
        print(F.MAGENTA + "changelog:\n" + F.LIGHTCYAN_EX + self.changelog + "\n")
        print(F.MAGENTA + "website: https://grapeuserbot.tiiny.site/")
        print(F.LIGHTCYAN_EX + "subscribe https://t.me/GrapeUserBot")
        await pyrogram.idle()
        await self.client.stop()


if __name__ == "__main__":
    grapeapi.logging()
    bot = GrapeUserBot()
    if not os.path.isfile("restart.txt"):
        asyncio.run(bot.requirements_load())
        bot.update()

    logging.info("Connecting grape api...")
    asyncio.run(bot.main())
