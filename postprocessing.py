import os
import asyncio
import csv
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
from TikTokApi import TikTokApi
import config

# Custom Domain
ghPagesURL = config.ghPagesURL

ms_token = os.environ.get("MS_TOKEN", None)

async def user_videos():
    with open('subscriptions.csv') as f:
        cf = csv.DictReader(f, fieldnames=['username'])
        for row in cf:
            user = row['username']
            print(f'Running for user \'{user}\'')

            fg = FeedGenerator()
            fg.id('https://www.tiktok.com/@' + user)
            fg.title(user + ' TikTok')
            fg.author({'name': 'Conor ONeill', 'email': 'conor@conoroneill.com'})
            fg.link(href='http://tiktok.com', rel='alternate')
            fg.logo(ghPagesURL + 'tiktok-rss.png')
            fg.subtitle('OK Boomer, all the latest TikToks from ' + user)
            fg.link(href=ghPagesURL + 'rss/' + user + '.xml', rel='self')
            fg.language('en')

            updated = None

            async with TikTokApi() as api:
                await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, headless=False)
                ttuser = api.user(user)
                try:
                    user_data = await ttuser.info()
                    print(user_data)
                except KeyError as e:
                    print(f"KeyError: {e} for user {user}")
                    continue

                async for video in ttuser.videos(count=10):
                    fe = fg.add_entry()
                    link = "https://tiktok.com/@" + user + "/video/" + video.id
                    fe.id(link)
                    ts = datetime.fromtimestamp(video.as_dict['createTime'], timezone.utc)
                    fe.published(ts)
                    fe.updated(ts)
                    updated = max(ts, updated) if updated else ts
                    if video.as_dict['desc']:
                        fe.title(video.as_dict['desc'][0:255])
                    else:
                        fe.title("No Title")
                    fe.link(href=link)
                    if video.as_dict['desc']:
                        fe.description(video.as_dict['desc'][0:255])
                    else:
                        fe.description("No Description")

                fg.updated(updated)
                fg.atom_file('rss/' + user + '.xml', pretty=True)  # Write the RSS feed to a file

if __name__ == "__main__":
    asyncio.run(user_videos())
