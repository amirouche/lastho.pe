import async_timeout


async def fetch(session, url):
    async with async_timeout.timeout(60):
        async with session.get(url) as response:
            return await response.text()
