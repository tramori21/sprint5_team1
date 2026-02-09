import asyncio
from elasticsearch import AsyncElasticsearch


async def wait_for_es(host: str, timeout: int = 30):
    es = AsyncElasticsearch(hosts=[host])
    for _ in range(timeout):
        try:
            if await es.ping():
                await es.close()
                return
        except Exception:
            pass
        await asyncio.sleep(1)
    await es.close()
    raise RuntimeError("Elasticsearch is not available")
