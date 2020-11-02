import argparse
import asyncio
import os
from functools import partial

import aiofiles
from aiohttp import web
from loguru import logger

from utils.project_logging import get_loguru_config


async def archivate(
    request,
    file_storage_path=os.getenv("FILE_STORAGE_PATH", "test_photos"),
    chunk_size=512 * 1024,
    delay_chunks_sending=0,
):

    archive_hash = request.match_info["archive_hash"]
    archive_path = os.path.join(file_storage_path, archive_hash)
    if not os.path.exists(archive_path):
        raise web.HTTPNotFound(reason="Архив не существует или был удален")

    response = web.StreamResponse()
    response.headers["Content-Disposition"] = f"Attachment;filename={archive_hash}.zip"
    await response.prepare(request)

    zip_process = await asyncio.create_subprocess_exec(
        "zip",
        "-r",
        "-",
        ".",
        cwd=archive_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        logger.debug("start downloading", extra={"archive_hash": archive_hash})
        while not zip_process.stdout.at_eof():
            archive_chunk = await zip_process.stdout.read(chunk_size)
            logger.debug(
                "Sending archive chunk ...", extra={"archive_hash": archive_hash}
            )
            await response.write(archive_chunk)
            await asyncio.sleep(delay_chunks_sending)
        else:
            logger.info("downloading complete", extra={"archive_hash": archive_hash})

    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Download was interrupted")
    except ConnectionResetError:
        logger.warning("Download failed - ConnectionResetError")
    except BaseException as err:
        logger.exception(f"Download was interrupted by exception: {err}")
    finally:
        logger.debug(f"proc code - {zip_process.returncode}")
        if zip_process.returncode is None:
            try:
                zip_process.kill()
                await zip_process.communicate()
                logger.debug(f"Archive process with PID: {zip_process.pid} was killed")
            except ProcessLookupError:
                logger.debug(f"Can not find process to kill it")

        response.force_close()

    return response


async def handle_index_page(request):
    async with aiofiles.open("index.html", mode="r") as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type="text/html")


def get_cli_args():
    parser = argparse.ArgumentParser(
        description="service for zipping and downloading files"
    )
    parser.add_argument("-l", "--logging", action="store_true", help="turn on logging")
    parser.add_argument(
        "-d",
        "--delay",
        type=int,
        default=os.getenv("DELAY_CHUNKS_SENDING", 0),
        help="delayed sending chunks of zip archive",
    )
    parser.add_argument(
        "-p",
        "--path",
        default=os.getenv("FILE_STORAGE_PATH", "test_photos"),
        help="path to storage with downloaded files",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = get_cli_args()
    if args.logging:
        logger.configure(
            **get_loguru_config(
                use_default_prod_configuration=False,
                level=os.getenv("LOGGING_LEVEL", "DEBUG"),
            )
        )
    else:
        logger.remove()

    app = web.Application(middlewares=[web.normalize_path_middleware()])
    app.add_routes(
        [
            web.get("/", handle_index_page),
            web.get(
                r"/archive/{archive_hash}/",
                partial(
                    archivate,
                    file_storage_path=args.path,
                    delay_chunks_sending=args.delay,
                ),
            ),
        ]
    )
    logger.info("server started")
    web.run_app(app)
    logger.info("server stopped")
