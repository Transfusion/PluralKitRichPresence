from cmd import Cmd

import sys
import asyncio
import aiohttp
import argparse
import concurrent.futures
import threading
import traceback

from importlib import util
from operator import attrgetter, itemgetter
from pypresence import AioPresence

loop = asyncio.new_event_loop()

parser = argparse.ArgumentParser(
    description="Show your PluralKit fronters in Discord Rich Presence"
)

parser.add_argument(
    "-id",
    "--system_id",
    metavar="system_id",
    type=str,
    help="Your PluralKit System ID",
    required=True,
)

parser.add_argument(
    "-cid",
    "--client_id",
    help="Discord Application Client ID",
    metavar="client_id",
    type=str,
    required=True,
)

parser.add_argument(
    "-t",
    "--interval",
    help="How frequently to poll for updates (in seconds), >= 15",
    metavar="interval",
    type=int,
    required=True,
)

parser.add_argument(
    "-f",
    "--fronters_parser",
    help="Path to a module that contains a function which converts the Fronters API response into the detail and state Rich Presence strings. Example: ./fronters_to_string.py",
    metavar="/path/to/parser.py",
    type=str,
    required=False,
)

parser.add_argument(
    "-api",
    help="PluralKit API Endpoint (default https://api.pluralkit.me)",
    metavar="api_endpoint",
    type=str,
    default="https://api.pluralkit.me",
    required=False,
)


def _default_fronters_to_string(system_info, fronters):
    members = fronters["members"]

    details = ", ".join(
        map(
            lambda member: member["display_name"]
            if member["display_name"] is not None
            else member["name"],
            members,
        )
        if len(members)
        else "(none)"
    )

    state = system_info["name"] if system_info["name"] is not None else "---"
    return {"details": details, "state": state}


interval = None


def main():
    global interval
    args = parser.parse_args()

    system_id, client_id, interval, api = attrgetter(
        "system_id", "client_id", "interval", "api"
    )(args)

    interval = max(15, interval)

    fronters_parser = _default_fronters_to_string
    if args.fronters_parser is not None:
        spec = util.spec_from_file_location("ftos", args.fronters_parser)
        ftos = util.module_from_spec(spec)
        spec.loader.exec_module(ftos)
        fronters_parser = ftos.fronters_to_string

    async def poll():
        global interval
        async with aiohttp.ClientSession() as session:
            RPC = AioPresence(client_id, loop=asyncio.get_running_loop())
            await RPC.connect()
            while True:
                try:
                    system_info = None
                    fronters = None

                    async with session.get(f"{api}/v1/s/{system_id}") as response:
                        system_info = await response.json()

                    async with session.get(
                        f"{api}/v1/s/{system_id}/fronters"
                    ) as response:
                        fronters = await response.json()

                    details, state = itemgetter("details", "state")(
                        fronters_parser(system_info, fronters)
                    )

                    print(
                        await RPC.update(
                            details=details,
                            state=state,
                        )
                    )
                    await asyncio.sleep(interval)
                except asyncio.CancelledError:
                    break
                except Exception:
                    traceback.print_exc()

            # await RPC.close()

    t = threading.Thread(target=lambda: loop.run_until_complete(poll()), daemon=True)

    class PKRPStatus(Cmd):
        def do_set_interval(self, line):
            """Set the poll interval (integer)"""
            global interval
            interval = int(line)

    cli = PKRPStatus()
    cli.prompt = "> "
    try:
        t.start()
        cli.cmdloop()

    except KeyboardInterrupt:
        # handle ctrl-c, graceful exit
        def stop():
            for task in asyncio.all_tasks(loop):
                task.cancel()

        loop.call_soon_threadsafe(stop)
        t.join()


if __name__ == "__main__":
    main()