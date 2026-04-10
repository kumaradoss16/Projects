import asyncio
import logging
from telegram import Update, BotCommand
from telegram.ext import (Application, CommandHandler, ContextTypes)
from config import BOT_TOKEN, CHECK_INTERVAL
from storage import (add_site, remove_site, get_sites, update_site, is_paused, set_paused)
from checker import check_site
from monitor import run_monitor, status_emoji

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Website Monitor Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "I'll watch your websites and alert you the *instant* anything changes.\n\n"
        "*Commands:*\n"
        "`/add <url> <name> [keyword]` — Add a site\n"
        "`/remove <url>` — Remove a site\n"
        "`/list` — Show all monitored sites\n"
        "`/status <url>` — Check a site right now\n"
        "`/statusall` — Check all sites immediately\n"
        "`/pause` — Pause monitoring\n"
        "`/resume` — Resume monitoring\n"
        "`/help` — Show this menu",
        parse_mode="Markdown"
    )

async def cmd_add(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    args = ctx.args
    if len(args) < 2:
        await update.message.reply_text(
            "Usage: `/add <url> <name> [keyword]`\n\n"
            "Example:\n"
            "`/add https://devspirehub.com DevspireHub`\n"
            "`/add https://mysite.com MyShop \"Add to Cart\"`",
            parse_mode="Markdown"
        )
        return 
    
    url = args[0]
    if not url.startswith("http"):
        url = "https://" + url
    
    name = args[1]
    keyword = " ".join(args[2:]) if len(args) > 2 else None

    if len(get_sites()) >= 50:
        await update.message.reply_text("Max 50 sites reached. Remove one first.")
        return 
    
    add_site(url, name. keyword)

    msg = (
        f"*Site added to watchlist!*\n"
        f"*Name:* {name}\n"
        f"*URL:* `{url}`\n"
    )

    if keyword:
        msg += f"*Monitoring keyword:* `{keyword}`\n"
    msg += f"*Check interval:* every {CHECK_INTERVAL}s"

    await update.message.reply_text(msg, parse_mode="Markdown")


async def cmd_remove(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Usage: `/remove <url>`",
            parse_mode="Markdown"
        )
        return 
    
    url = ctx.args[0]
    if remove_site(url):
        await update.message.reply_text(f"Removed: `{url}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("URL not found in watchlist.")


async def cmd_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    sites = get_sites()
    if not sites:
        await update.message.reply_text("No sites being monitored. Use /add to start.")
        return 
    
    paused_tag = " ⏸ *PAUSED* " if is_paused() else ""
    msg = f" *Monitored Sites*{paused_tag}\n{'━'*30}\n"

    for url, info in sites.items():
        emoji = status_emoji(info.get("status", "unknown"))
        rt = f"{info['response_time']}ms" if info.get("response_time") else "N/A"
        kw = f"`{info['keyword']}" if info.get("keyword") else ""
        msg += (
            f"{emoji} *{info['name']}*{kw}\n"
            f"   └ `{url}`\n"
            f"   └ ⏱ {rt} | 🕐 {info.get('last_checked') or 'Never'}\n\n"
        )

        await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Usage: `/status <url>`", parse_mode="Markdown")
        return
    
    url = ctx.args[0]
    sites = get_sites()
    keyword = sites.get(url, {}).get("keyword")

    await update.message.reply_text(f"Checking `{url}`...", parse_mode="Markdown")
    result = await check_site(url, keyword)

    emoji = status_emoji(result["status"])
    msg = (
        f"{emoji} *Live Check Result*\n"
        f"{'─'*30}\n"
        f"`{url}\n"
        f"Status: *{result['status'].upper()}*\n"
        f"HTTP Code: `{result['status_code'] or 'N/A'}\n"
        f"Response: `{result['response_ms']} ms`\n"
        f"Checked: {result['checked_at']}\n"
    )

    if result.get("error"):
        msg += f"Error: `{result['error']}\n"
    if result.get("keyword") and result.get("keyword_found") is not None:
        found = "Found" if result["keyword_found"] else "Not found"
        msg += f"Keyword: {found}\n"

    await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)


async def cmd_status_all(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    sites = get_sites()
    if not sites:
        await update.message.reply_text("No sites to check.")
        return 
    
    await update.message.reply_text(f"Checking {len(sites)} site(s)...")

    msg = "*Live Status - All Sites*\n" + "━" * 30 + "\n"
    for url, info in sites.items():
        result = await check_site(url, info.get("keyword"))
        emoji = status_emoji(result["status"])
        update_site(url, status=result["status"], response_time=result["response_ms"], last_checked=result["checked_at"])
        rt = f"{result['response_ms']}ms" if result["response_ms"] else "N/A"
        msg += f"{emoji} * {info['name']}* — `{rt}`\n   `{url}`\n\n"

    await update.message.reply_text(msg, parse_mode="Markdown",disable_notification=True)


async def cmd_pause(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    set_paused(True)
    await update.message.reply_text("⏸ Monitoring *paused*. Use /resume to restart.",
                                    parse_mode="Markdown")
    
async def cmd_resume(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    set_paused(False)
    await update.message.reply_text("Monitoring *resumed*!", parse_mode="Markdown")


async def post_init(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start",     "Show welcome & help"),
        BotCommand("add",       "Add a site to monitor"),
        BotCommand("remove",    "Remove a site"),
        BotCommand("list",      "List all monitored sites"),
        BotCommand("status",    "Live check one site"),
        BotCommand("statusall", "Live check all sites"),
        BotCommand("pause",     "Pause monitoring"),
        BotCommand("resume",    "Resume monitoring"),
    ])

    asyncio.create_task(run_monitor(app))
    print("Bot is live and monitoring started!")


def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("add", cmd_add))
    app.add_handler(CommandHandler("remove", cmd_remove))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("statusall", cmd_status_all))
    app.add_handler(CommandHandler("pause", cmd_pause))
    app.add_handler(CommandHandler("resume", cmd_resume))

    print("Starting Website Monitor Bot...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()