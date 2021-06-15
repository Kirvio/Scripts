import aiohttp
import asyncio
import aiofiles
import os
 
async def download_coroutine(session, url):
    epgsave = 'C:\Scripts'
    async with session.get(url) as response:
        if response.status == 200: 
            f = await aiofiles.open((os.path.join(epgsave, "epg.zip")), mode='wb')
            await f.write(await response.read())
            await f.close()
            return await response.release()
 
async def main(loop):
    url = 'https://iptvx.one/EPG'
 
    async with aiohttp.ClientSession(loop=loop) as session:
        task = download_coroutine(session, url) 
        await asyncio.gather(task)
 
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))