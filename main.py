from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from regex import escape, findall, search, split, sub
from dotenv import load_dotenv
from os import getenv, system
from bs4 import BeautifulSoup
from telegram import Update
from html import unescape
from requests import get
from time import time

load_dotenv()
global DEBUGGING
AUTHORIZED_USERS: list[str] = [x for x in getenv("AUTHORIZED_USERS", "").split(",") if x]
TELEGRAM_TOKEN: str = getenv("TELEGRAM_TOKEN") or exit("TELEGRAM_TOKEN not defined in .env")
DEBUGGING: bool = str(getenv("DEV")).capitalize() == "True"
system("cls")

async def get_response(post_url: str):
    response = ""
    try: response = get(post_url)
    except Exception as e:
        with open(f"logs.log", "a", encoding="utf-8") as f:
            f.write(f"Error: {e} - {post_url}\n")
            print("An error has occurred. See log for more info.")
        return "instagram_unavailable"
    if DEBUGGING:print("Request was successful!" if response.status_code == 200 else f"Status code: {response.status_code}")
    if DEBUGGING:
        with open(f"page_content.html", "w", encoding="utf-8") as f:
            f.write(unescape(response.text))
            print("HTML content was saved!")
    return response

async def get_data(datas: dict[str, str | list], soup: BeautifulSoup):
    result = soup.find("meta", {"name": "twitter:title"})
    if not result:
        with open(f"logs.log", "a", encoding="utf-8") as f:
            f.write(f"Error: link_broken_or_post_removed")
            print("An error has occurred. See log for more info.")
        return "link_broken_or_post_removed"
    assert result is not None, f'Tag "meta title" not found'
    tag = str(result.get("content"))

    datas["username"] = m.group() if (m := search(r"(?<=\(@)[\w.]*(?=\))", tag)) else ""
    datas["name"] = m.group() if (m := search(r"^.*(?=\s\(@)", tag)) else ""

    result = soup.find("meta", {"name": "description"})
    assert result is not None, f"Tag \"meta title\" not found"
    tag = str(result.get("content"))

    datas["description"] = m.group() if (m := search(r"(?<=\")[^\"]*(?=.)", tag)) else ""
    datas["comments"] = m.group() if (m := search(r"(?<=,\s)[\w\s.]*(?=\s-)", tag)) else ""
    datas["likes"] = m.group() if (m := search(r"[\w\s.]*(?=,)", tag)) else ""
    datas["date"] = m.group() if (m := search(r"(?<=on )[\w\s,]*(?=:\s\")", tag)) else ""
    return datas

async def md_instagram_links(text: str) -> str:
    text = "".join([sub(r"(\w)\.(\w)", r"\1\u200b.\2", p) if not p.startswith("<") else p for p in split(r"(<[^>]+>)", text)])
    hashtag, at = set(findall(r"#[\p{L}\p{M}\p{N}\p{Emoji}_]+", text)), set(findall(r"@[\w.]+", text))
    if hashtag: text = (t := text, [t := sub(fr"{escape(h)}(?=\s|$)", f"[{h}](instagram.com/explore/search/keyword/?q=%23{h[1:]})", t) for h in hashtag], t)[-1]
    return (t := text, [t := sub(fr"{escape(a)}(?=\s|$)", f"[{a}](instagram.com/{a[1:]})", t) for a in at], t)[-1] if at else text

async def dedent_remover(text: str) -> str:
    while "\n " in text: text = text.replace("\n ", "\n")
    return text

async def insta_geter(post_url: str):
    datas:dict[str,str|list[str]]={}
    response = await get_response(post_url)
    if isinstance(response, str):
        datas["error"] = response
        return datas
    soup = BeautifulSoup(response.content, "html.parser")
    data = await get_data(datas, soup)
    if isinstance(data, str):
        datas["error"] = data
        return datas
    datas |= data
    return datas

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat
    if ((update.effective_chat.username in AUTHORIZED_USERS) if AUTHORIZED_USERS else True):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hi {update.effective_chat.first_name}!\nHow are you?")

async def insta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_message
    assert update.effective_chat
    assert update.message
    start = time() if DEBUGGING else 0
    if ((update.effective_chat.username in AUTHORIZED_USERS) if AUTHORIZED_USERS else True) and update.message.text:
        await context.bot.set_message_reaction(chat_id=update.effective_chat.id, message_id=update.effective_message.id, reaction=["👀"])
        if context.user_data is not None:
            url_received = update.message.text[7:]
            last_url = context.user_data.get("last_url", "")
            datas = await insta_geter(url_received)
            if not "error" in datas:
                message_to_user = await dedent_remover(f"""
                    The [post]({url_received}) has the following data:
                    Name: {datas["name"]}
                    Username: [@{datas["username"]}](instagram.com/{datas["username"]})
                    Description: {await md_instagram_links(str(datas["description"]))}
                    
                    {datas["likes"]}
                    {datas["comments"]}
                    Publication date: {datas["date"]}
                    {f"{time()-start:.2f}s" if DEBUGGING else ""}""")
            else:
                match datas["error"]:
                    case "instagram_unavailable": message_to_user = ("Apparently Instagram is currently unavailable.")
                    case "link_broken_or_post_removed": message_to_user = "Check the link again, if everything is ok then the post has been removed."
                    case _: message_to_user = "An error has ocurred."
                message_to_user += f"\nPlease, try again{" later." if last_url and last_url == url_received else "."}"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message_to_user, parse_mode="Markdown")
            context.user_data["last_url"] = url_received

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    [application.add_handler(CommandHandler(c, globals()[c])) for c in ["start", "insta"]]
    print("Working")
    application.run_polling()

main() if __name__ == "__main__" else quit("Tsc, tsc, tsc... Not like that!")
