from keep_alive import keep_alive  # ← 追加する！
import os
import discord
from discord.ext import commands

import discord
from discord.ext import commands
from collections import Counter

intents = discord.Intents.default()
intents.message_content = True  
bot = commands.Bot(command_prefix="!", intents=intents)

game_active = False
tags = []
rankings = []
current_rank = 12
score_table = [15, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
scores = {}

# タグ数に応じた最大出現回数
MAX_OCCURRENCES = {
    6: 2,
    4: 3,
    3: 4,
    2: 6
}
VALID_TAG_COUNTS = {6, 4, 3, 2}  # 許可されたタグ数

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")

@bot.command()
async def start(ctx):
    global game_active, tags, rankings, current_rank, scores
    game_active = True
    tags = []
    rankings = []
    current_rank = 12
    scores = {}
    await ctx.send("チームのタグを入力してください（半角スペース区切り）")

@bot.command()
async def end(ctx):
    global game_active
    game_active = False
    if scores:
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        score_message = "**最終スコア**\n"
        top_score = sorted_scores[0][1]
        for i, (team, score) in enumerate(sorted_scores):
            diff = f" (+{abs(score - top_score)})" if i > 0 else ""
            score_message += f"{team}: {score}点{diff}\n"
        await ctx.send(score_message)
    else:
        await ctx.send("終了しました。")

@bot.command()
async def back(ctx):
    global rankings, current_rank, scores
    if rankings:
        rankings.pop()
        current_rank += 1
        scores.clear()

        # 再計算
        for ranking in rankings:
            for i, team_tag in enumerate(ranking):
                scores[team_tag] = scores.get(team_tag, 0) + score_table[i]

        score_message = "**現在のスコア**\n"
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_score = sorted_scores[0][1] if sorted_scores else 0
        for i, (team, score) in enumerate(sorted_scores):
            diff = f" (+{abs(score - top_score)})" if i > 0 else ""
            score_message += f"{team}: {score}点{diff}\n"

        await ctx.send(score_message + f"\n@{current_rank}")
    else:
        await ctx.send("戻せる入力がありません。")

@bot.event
async def on_message(message):
    global game_active, tags, rankings, current_rank, scores

    if message.author == bot.user:
        return  

    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    if game_active:
        if not tags:
            input_tags = message.content.split()

            # **タグの個数チェック**
            if len(input_tags) not in VALID_TAG_COUNTS:
                await message.channel.send("タグの数が不正です。2, 3, 4, 6 個のいずれかにしてください。")
                return

            unique_initials = set()

            # **タグの重複チェック**
            for tag in input_tags:
                if tag[0] in unique_initials:
                    await message.channel.send(f"'{tag[0]}' の頭文字が重複しています。異なるタグを入力してください。")
                    return
                unique_initials.add(tag[0])

            tags = input_tags
            await message.channel.send("タグを登録しました！順位を12文字で入力してください。")

        elif len(message.content) == 12:
            unique_tags = {tag[0] for tag in tags}  

            # **タグにない文字が含まれていないかチェック**
            if any(char not in unique_tags for char in message.content):
                await message.channel.send("タグにない文字が含まれています。正しい順位を入力してください。")
                return

            # **同じ文字の出現回数をチェック**
            tag_count = len(tags)
            char_counts = Counter(message.content)
            max_occurrence = MAX_OCCURRENCES.get(tag_count, 2)  # デフォルト2

            for char, count in char_counts.items():
                if count > max_occurrence:
                    await message.channel.send(f"'{char}' が {count} 回登場しています。{max_occurrence} 回までにしてください。")
                    return

            rankings.append(message.content)
            for i, team_tag in enumerate(message.content):
                scores[team_tag] = scores.get(team_tag, 0) + score_table[i]

            score_message = "**現在のスコア**\n"
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            top_score = sorted_scores[0][1]
            for i, (team, score) in enumerate(sorted_scores):
                diff = f" (+{abs(score - top_score)})" if i > 0 else ""
                score_message += f"{team}: {score}点{diff}\n"

            current_rank -= 1
            if current_rank >= 1:
                await message.channel.send(score_message + f"\n@{current_rank}")
            else:
                await message.channel.send(score_message + "\nすべての順位が入力されました！")
                game_active = False  
        else:
            await message.channel.send("順位は12文字で入力してください。")

import os
from dotenv import load_dotenv

load_dotenv()  # .env ファイルを読み込む
TOKEN = os.getenv("TOKEN")  # TOKEN を取得

keep_alive()  # サーバーを起動
bot.run(os.getenv("TOKEN"))  # Botを起動

bot.run(TOKEN)

from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

from keep_alive import keep_alive

keep_alive()  # サーバーを起動
