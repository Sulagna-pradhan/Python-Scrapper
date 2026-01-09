from telethon import TelegramClient, events
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import FloodWaitError
import asyncio, random, re, time

api_id =123
api_hash = "" 
session = "safe_forward_session"

HISTORY_LIMIT = 100
DAILY_LIMIT = 900
MIN_DELAY = 5
MAX_DELAY = 9


client = TelegramClient(session, api_id, api_hash)
sent_today = 0
day_start = time.time()


def parse_input(link: str):
    link = link.strip()
    if "t.me/+" in link:
        return {"type": "private", "hash": link.split("+")[1]}
    link = re.sub(r"https?://t\.me/", "", link)
    return {"type": "public", "value": link.lstrip("@")}


SOURCE = parse_input(input("Enter SOURCE public channel link: "))
DEST = parse_input(input("Enter DESTINATION channel link or username: "))


def reset_daily():
    global sent_today, day_start
    if time.time() - day_start > 86400:
        sent_today = 0
        day_start = time.time()


async def safe_sleep():
    await asyncio.sleep(random.randint(MIN_DELAY, MAX_DELAY))


async def resolve_dest():
    if DEST["type"] == "private":
        await client(ImportChatInviteRequest(DEST["hash"]))
        return DEST["hash"]
    return DEST["value"]


async def forward_old(dest):
    global sent_today
    print(f"📜 Forwarding last {HISTORY_LIMIT} messages safely...")

    async for msg in client.iter_messages(SOURCE["value"], limit=HISTORY_LIMIT, reverse=True):
        reset_daily()

        if sent_today >= DAILY_LIMIT:
            print("🛑 Daily limit reached")
            return

        if not msg or msg.action:
            continue  # skip MessageService

        try:
            await msg.forward_to(dest)
            sent_today += 1
            print(f"✅ Old forwarded ({sent_today}/{DAILY_LIMIT})")
            await safe_sleep()

        except FloodWaitError as e:
            print(f"⏳ FloodWait {e.seconds}s")
            await asyncio.sleep(e.seconds)

        except Exception as e:
            print("❌ Old msg error:", e)


@client.on(events.NewMessage(chats=SOURCE["value"]))
async def forward_new(event):
    global sent_today
    reset_daily()

    if sent_today >= DAILY_LIMIT:
        return

    if event.message.action:
        return

    try:
        await event.message.forward_to(dest_entity)
        sent_today += 1
        print(f"➡️ New forwarded ({sent_today}/{DAILY_LIMIT})")
        await safe_sleep()

    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)

    except Exception as e:
        print("❌ New msg error:", e)


async def main():
    await client.start()
    global dest_entity
    dest_entity = await resolve_dest()

    await forward_old(dest_entity)
    print("🟢 SAFE MODE ACTIVE — listening...")
    await client.run_until_disconnected()


client.loop.run_until_complete(main())
