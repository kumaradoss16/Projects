import asyncio
from datetime import datetime
from checker import check_site
from storage import get_sites, update_site, is_paused
from config import CHECK_INTERVAL, CHAT_ID

def status_emoji(status: str) -> str:
    return {"up": "✅", "down": "🔴", "keyword_missing": "⚠️", "unknown": "❓"}.get(status, "❓")

async def run_monitor(app):
    print(f"🔍 Monitor started — checking every {CHECK_INTERVAL}s")

    while True:
        if not is_paused():
            sites = get_sites()

            for url, info in sites.items():
                prev_status = info.get("status", "unknown")
                result = await check_site(url, info.get("keyword"))
                new_status = result["status"]

                update_site(
                    url,
                    status=new_status,
                    last_checked=result["checked_at"],
                    response_time=result["response_ms"],
                    failures=info.get("failures", 0) + (1 if new_status != "up" else 0)
                )

                if new_status != prev_status:
                    await send_alert(app, url, info["name"], prev_status,
                                     new_status, result)

        await asyncio.sleep(CHECK_INTERVAL)

async def send_alert(app, url: str, name: str, prev: str, curr: str, result: dict):
    emoji = status_emoji(curr)
    prev_emoji = status_emoji(prev)

    if curr == "ip":
        header = f"✅ *SITE RECOVERED*"
        color_word = "is back ONLINE"
    elif curr == "down":
        header = f"🔴 *SITE DOWN*"
        color_word = "went OFFLINE"
    else:
        header = f"⚠️ *CONTENT CHANGED*"
        color_word = "is missing expected content"

    msg = (
        f"{header}\n"
        f" {'─' * 30}\n"
        f"📌 *Site:* {name}\n"
        f"🔗 *URL:* `{url}`\n"
        f"📊 *Status:* {prev_emoji} → {emoji}  _{color_word}_\n"
        f"⏱ *Response:* {result['response_ms']} ms\n"
        f"🕐 *Time:* {result['checked_at']}\n"
    )

    if result.get("error"):
        msg += f"❌ *Error:* `{result['error']}`\n"

    if curr != "up":
        msg += f"\n🔁 Rechecking every {CHECK_INTERVAL}s until recovery..."

    await app.bot.send_message(
        chat_id=CHAT_ID,
        text=msg,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    print(f"  📤 Alert sent: {name} → {curr}")