from re import L, match
from threading import Thread, Timer, Event
from flask import Flask
import json
import requests
import discord
import datetime
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import os

DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
URL_COIN_GUECKO = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&localization=false'

app = Flask(__name__)

count: int = 0
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.content.startswith('!'):
        if message.author == client.user:
            return
        if message.content.startswith('!cryptoinfo:'):
            coin = message.content[12:]
            URL = 'https://api.coingecko.com/api/v3/coins/'+str(coin)+'?vs_currency=usd&localization=false'
            response = requests.get(URL)
            content_json = response.content.decode('utf-8').replace("'", '"')
            content_dict = json.loads(content_json)
            symbol = content_dict['symbol']
            market_data = content_dict['market_data']
            price = market_data['current_price']['usd']
            high_24h = market_data['high_24h']['usd']
            low_24h = market_data['low_24h']['usd']
            percent_change_24h = market_data['price_change_percentage_24h']
            percent_change_7d = market_data['price_change_percentage_7d']
            percent_change_30d = market_data['price_change_percentage_30d']
            picture = content_dict['image']["small"]
            embed = discord.Embed()
            embed.set_image(url=picture)
            await message.channel.send(embed=embed)
            await message.channel.send(
                (
                    "Crypto: {0} ({1})\n"
                    "Preço atual: US${2}\n\n"
                    "Variação percentual do preço:\n"
                    "\t24 horas: {3}%\n"
                    "\t7 dias: {4}%\n"  
                    "\t30 dias: {5}%\n"  
                ).format(
                    coin,
                    symbol,
                    str(round(price,2)),
                    round(percent_change_24h,2),
                    round(percent_change_7d,2),
                    round(percent_change_30d,2)
                )
            )           

        if message.content.startswith('!cryptochart:'):
            txt = message.content[13:]
            coin, period = txt.split('-')[0], txt.split('-')[1]
            URL = 'https://api.coingecko.com/api/v3/coins/'+str(coin)+'/market_chart?vs_currency=usd&days='+str(period)
            response = requests.get(URL)
            content_json = response.content.decode('utf-8').replace("'", '"')
            content_dict = json.loads(content_json)
            prices = []
            date = []
            now = datetime.datetime.now()
            start = now + datetime.timedelta(hours=-30)
            for i in range(len(content_dict['prices'])):
                prices.append(content_dict['prices'][i][1])
                date.append(start+datetime.timedelta(hours=i))
            data = {'prices': prices, 'date': date}
            df = pd.DataFrame(data=data)
            sns.set(rc={'figure.figsize':(18,8)})
            sns.set_style("whitegrid")
            axes = sns.lineplot(x=df['date'],y=df['prices'])
            axes.set_xlabel('')
            axes.set_ylabel('')
            plt.savefig('cryptochart.png')
            plt.close()
            plt.cla()
            plt.clf()
            await message.channel.send(file=discord.File('cryptochart.png'))
            




            # prices = content_dict['prices']
            # prices[]

            # fig = go.Figure(data=[go.Candlestick(x=df['Date'],
            # open=df['AAPL.Open'],
            # high=df['AAPL.High'],
            # low=df['AAPL.Low'],
            # close=df['AAPL.Close'])])


          
    else:
        return''
client.run(DISCORD_BOT_TOKEN)



if __name__ == '__main__':
    app.run()  # run our Flask app

