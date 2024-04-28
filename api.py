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
        def get_prefix() -> str:
            if not os.path.isfile("files/prefix"):
                with open("files/prefix", "w") as file:
                    file.write("!")
                    file.close()
                    return "!"
            else:
                with open("files/prefix", "r") as file:
                    return file.read()

        @staticmethod
        async def set_prefix(prefix) -> bool:
            try:
                with open("files/prefix", "w") as file:
                    file.write(prefix)
                    file.close()
                    return True

            except:
                return False

    class db:
        def __init__(self):
            self.conn = None

        async def connect(self):
            import aiosqlite
            self.conn = await aiosqlite.connect('files/grape.db')

        async def close(self):
            await self.conn.close()

        async def execute(self, query, *args):
            async with self.conn.execute(query, args) as cursor:
                return await cursor.fetchall()

        async def commit(self):
            await self.conn.commit()


class command:
    def __init__(self, command_: str, desc: str):
        self.command = command_
        self.desc = desc


class module:
    def __init__(self, name: str, desc: str, file: str, version: float, commands: list):
        self.name = name
        self.desc = desc
        self.file = file
        self.version = version
        self.commands = commands

    def get_commands(self):
        commands = []
        for command_ in self.commands:
            commands.append(command_)
        return commands


modules = []


class modules_actions:
    @staticmethod
    def get_modules():
        return modules

    @staticmethod
    def add_module(module: module):
        modules.append(module)

    @staticmethod
    def get_module(module_name: str):
        for module in modules:
            if module.name == module_name:
                return module

        return None
