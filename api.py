import os


class grapeapi:
    @staticmethod
    async def import_library(library_name: str, update: bool = True, check: bool = True, console: bool = False):
        import asyncio
        command = ['pip', 'install', library_name]
        if update:
            command.append('--update')
        if not console:
            command.append('--quiet')

        if check:
            get_list = await asyncio.create_subprocess_exec("pip", "list", stdout=asyncio.subprocess.PIPE,
                                                            stderr=asyncio.subprocess.PIPE)
            output, _ = await get_list.communicate()
            if library_name.encode() not in output:
                execute = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE,
                                                               stderr=asyncio.subprocess.PIPE)
                await execute.communicate()
                return execute.returncode
            else:
                return
        else:
            execute = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE,
                                                           stderr=asyncio.subprocess.PIPE)
            await execute.communicate()
            return execute.returncode

    @staticmethod
    async def restart(message=None):
        import sys

        f = open("restart.txt", "w")
        if message:
            if message.chat.username:
                f.write(str(message.chat.username))
            else:
                f.write(str(message.chat.id))
        else:
            f.write("me")

        f.close()
        os.execvp(sys.executable, [sys.executable, *sys.argv])

    class prefix:
        @staticmethod
        async def get_prefix() -> str:
            db = grapeapi.db()
            await db.connect()
            await db.execute('CREATE TABLE IF NOT EXISTS prefix (prefix TEXT)')
            await db.commit()
            row = await db.execute("SELECT prefix FROM prefix")
            await db.close()
            if row:
                return row[0]
            else:
                return "!"

        @staticmethod
        async def set_prefix(prefix) -> bool:
            db = grapeapi.db()
            await db.connect()
            await db.execute('CREATE TABLE IF NOT EXISTS prefix (prefix TEXT)')
            await db.commit()
            await db.execute("INSERT INTO prefix (prefix) VALUES (?)", (prefix,))
            await db.close()
            return True

    class modules:
        def __init__(self):
            self.modules = {}
            self.commands = {}
            self.files = {}
            self.modules_count = len(self.modules)

        @staticmethod
        async def add_module(module_name: str, filename: str):
            grapeapi.modules.modules[module_name] = filename

        @staticmethod
        def add_command(module_name: str, command_name: str, help_command: str):
            grapeapi.modules.commands.setdefault(module_name, {})
            grapeapi.modules.commands[module_name][command_name] = help_command

        @staticmethod
        def get_module_commands(module_name):
            if module_name in grapeapi.modules.commands:
                return grapeapi.modules.commands[module_name]
            else:
                return {}

        @staticmethod
        def get_file_by_module(module_name):
            if module_name in grapeapi.modules.modules:
                dir_name, file_name = os.path.split(grapeapi.modules.modules[module_name])
                last_folder = os.path.basename(dir_name)
                return os.path.join(last_folder, file_name)
            else:
                return None

        @staticmethod
        def add_file(module_name: str, file_name: str):
            grapeapi.modules.files.setdefault(module_name, {})
            var = grapeapi.modules.files[module_name][file_name]

        @staticmethod
        def load_module(link):
            import requests
            filename = os.path.basename(link)
            code = requests.get(link).text
            return filename, code

        @staticmethod
        def upload_module(module_name: str):
            if module_name in grapeapi.modules.modules:
                return grapeapi.modules.modules[module_name]
            else:
                return None

        @staticmethod
        def remove_module(module_name: str):
            if module_name in grapeapi.modules.modules:
                try:
                    os.remove(grapeapi.modules.modules[module_name])
                    return True
                except Exception as e:
                    print(e)
                    return False
            else:
                return None

    class db:
        def __init__(self):
            self.conn = None

        async def connect(self):
            import aiosqlite
            self.conn = await aiosqlite.connect('grape.db')

        async def close(self):
            await self.conn.close()

        async def execute(self, query, *args):
            async with self.conn.execute(query, args) as cursor:
                return await cursor.fetchall()

        async def commit(self):
            await self.conn.commit()