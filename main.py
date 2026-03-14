# pyright: reportOptionalMemberAccess=false
from re import search
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from os import getenv, system
from html import unescape
from requests import get
from time import time

load_dotenv()
global DEBUGGING
AUTHORIZED_USERS: list[str] = [x for x in getenv("AUTHORIZED_USERS", "").split(",") if x]
TELEGRAM_TOKEN: str = getenv("TELEGRAM_TOKEN") or exit("TELEGRAM_TOKEN not defined in .env")
DEBUGGING: bool = getenv("DEV").capitalize() == "True"
system("cls")


async def get_response(post_url: str):
    response = ""
    try: response = get(post_url)
    except Exception as e:
        with open(f"logs.log", "a", encoding="utf-8") as f:
            f.write(f"Error: {e} - {post_url}\n")
            print("An error has occurred. See log for more info.")
        return "instagram_unavailable"
    if DEBUGGING:
        print( "Request was successful!" if response.status_code == 200 else f"Status code: {response.status_code}" )
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

    datas["username"] = search(r"(?<=@)\w*", tag).group()
    datas["name"] = search(r"^[\w\d\s.]*(?=\s\|)", tag).group()

    result = soup.find("meta", {"name": "description"})
    assert result is not None, f'Tag "meta title" not found'
    tag = str(result.get("content"))
    description_start = tag.index('"') + 1
    description_end = tag.index('"', description_start)
    likes_comments_end = tag.index("-")
    datas["likes"], datas["comments"] = tag[:likes_comments_end].split(", ")
    datas["comments"] = datas["comments"].strip()
    datas["description"] = tag[description_start:]
    datas["description"] = tag[:description_end]
    datas["description"] = tag[description_start:description_end].strip()
    datas["date"] = tag[likes_comments_end: description_start - 1]
    datas["date"] = (
        datas["date"]
        .replace("-", "")
        .replace(datas["username"][1:], "")
        .replace("on", "")
        .replace(":", "")
        .strip()
    )
    return datas


async def md_instagram_links(origin_text: str) -> str:
    text = origin_text
    count_of_hashtag = text.count("#")
    count_of_at = text.count("@")
    hashtag: list[str] = []
    at: list[str] = []
    for _ in range(count_of_hashtag):
        start = text.index("#")
        immediate_space:int = 0
        end=0
        while 1:
            try:
                slash_index = text.index("\n", start+immediate_space)
                try:
                    space_index = text.index(" ", start+immediate_space)
                    end = slash_index if slash_index < space_index else space_index
                except:
                    end = slash_index
            except:
                try:
                    space_index = text.index(" ", start+immediate_space)
                    end = space_index
                except:
                    end = 0
            if text[start+immediate_space+1:end] or not end: break
            else:immediate_space+=1

        hashtag.append(text[start:end]) if end else hashtag.append(
            text[start:])
        text = text.replace(hashtag[-1], "", 1)
    for _ in range(count_of_at):
        start = text.index("@")
        immediate_space:int = 0
        end=0
        while 1:
            try:
                slash_index = text.index("\n", start+immediate_space)
                try:
                    space_index = text.index(" ", start+immediate_space)
                    end = slash_index if slash_index < space_index else space_index
                except:
                    end = slash_index
            except:
                try:
                    space_index = text.index(" ", start+immediate_space)
                    end = space_index
                except:
                    end = 0
            if text[start+immediate_space+1:end] or not end: break
            else:immediate_space+=1
        at.append(text[start:end]) if end else at.append(text[start:])
        text = text.replace(at[-1], "", 1)
    for i in range(count_of_hashtag):
        origin_text = origin_text.replace(
            hashtag[i],
            f"[{hashtag[i].replace(" ", "")}](instagram.com/explore/search/keyword/?q=%23{hashtag[i][1:].replace(" ", "")})", 1)
    for i in range(count_of_at):
        origin_text = origin_text.replace(
            at[i], f"[{at[i].replace(" ", "")}](instagram.com/{at[i][1:].replace(" ", "")})", 1)
    return origin_text


async def dedent_remover(text: str) -> str:
    while "\n " in text:
        text = text.replace("\n ", "\n")
    return text


async def insta_geter(post_url: str):
    datas: dict[str, str | list[str]] = {}
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
    if (
        (update.effective_chat.username in AUTHORIZED_USERS)
        if AUTHORIZED_USERS
        else True
    ):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Hi {update.effective_chat.first_name}!\nHow are you?",
        )


async def insta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time() if DEBUGGING else 0
    if (
        (update.effective_chat.username in AUTHORIZED_USERS)
        if AUTHORIZED_USERS
        else True
    ) and update.message.text:
        await context.bot.set_message_reaction(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.id,
            reaction=["👀"],
        )
        if context.user_data is not None:
            url_received = update.message.text[7:]
            last_url = context.user_data.get("last_url", "")
            datas = await insta_geter(url_received)
            if not "error" in datas:
                message_to_user = await dedent_remover(
                    f"""
                        The [post]({url_received}) has the following data:
                        Name: {datas["name"]}
                        Username: [{datas["username"]}](instagram.com/{datas["username"][1:]})
                        Description: {await md_instagram_links(str(datas["description"]))}
                        {datas["likes"]}
                        {datas["comments"]}
                        Publication date: {datas["date"]}
                        {f"{time()-start:.2f}s" if DEBUGGING else ""}"""
                )
            else:
                match datas["error"]:
                    case "instagram_unavailable":
                        message_to_user = (
                            "Apparently Instagram is currently unavailable."
                        )
                    case "link_broken_or_post_removed":
                        message_to_user = "Check the link again, if everything is ok then the post has been removed."
                    case _:
                        message_to_user = "An error has ocurred."
                message_to_user += f"\nPlease, try again{" later." if last_url and last_url == url_received else "."}"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message_to_user,
                parse_mode="Markdown",
            )
            context.user_data["last_url"] = url_received


def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    commands = ["start", "insta"]
    [application.add_handler(CommandHandler(c, globals()[c]))
     for c in commands]
    print("Working")
    application.run_polling()


main() if __name__ == "__main__" else quit("Tsc, tsc, tsc... Not like that!")
