import asyncio
import logging
import functools
import requests
import concurrent.futures


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sync_loader(url):
    logger.info(f"Sync download {url}")
    return requests.get(url).json()


async def coro_loader(url):
    fn = functools.partial(sync_loader, url)
    loop = asyncio.get_event_loop()
    logger.info(f"start download async {url}")
    return await loop.run_in_executor(None, fn)


async def waiter(pending_tasks):
    wait_for = 60
    while not all(map(lambda x: x.done(), pending_tasks.values())) and wait_for > 0:
        logger.info("Waiting for pending task results...")
        await asyncio.sleep(1)
        wait_for -= 1
    for api_id, task in pending_tasks.items():
        if not task.done():
            task.cancel()
            logger.warning(f"Postprocess {api_id} task was cancelled.")
            continue
        logger.info(f"Postprocess pending task api_id: {api_id}; {task.result()}")

async def download_async():
    urls = {api_id: "http://localhost:8001/url/{0}".format(api_id)
            for api_id in [3,4]}

    urls[5] = "http://localhost:8001/url/0"  # for example 5th url its a fast API

    pending_tasks = {}
    res = {}

    for api_id, url in urls.items():
        task = asyncio.Task(coro_loader(url))
        try:
            res = await asyncio.wait_for(asyncio.shield(task), timeout=1)
        except concurrent.futures.TimeoutError:
            pending_tasks[api_id] = task
            logger.info(f"Add download task for {url} to pending tasks list.")

        if not res:
            continue
        else:
            logger.info(f"Success with send data to {url}, in pending_tasks now"
                        f" are {len(pending_tasks)} tasks.")
            break

    loop = asyncio.get_event_loop()
    loop.create_task(waiter(pending_tasks))


loop = asyncio.get_event_loop()
loop.create_task(download_async())
loop.run_forever()
