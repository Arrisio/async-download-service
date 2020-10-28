import subprocess
import asyncio
import aiofiles

async def zzp():
    proc = await asyncio.create_subprocess_exec(
        "zip",
        "-r",
        # "results/rez.zip",
        "-",
        "test_photos",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # proc  = await asyncio.create_subprocess_shell("zip -r results/rez.zip test_photos")
    # stdout, stderr = await proc.communicate()

    async with aiofiles.open('results/rez.zip', 'wb+') as fh:
        while not proc.stdout.at_eof():
            archive_chunk = await proc.stdout.read(2048)
            await  fh.write(archive_chunk)


asyncio.run(zzp())
# pr = asyncio.create_subprocess_exec("zip", *["results/rez.zip", "test_photos"])
# pr = asyncio.create_subprocess_shell("zip -r results/rez.zip test_photos")
# loop = asyncio.get_event_loop()
# loop.run(pr)

# subprocess.run(["zip", "-r", "-", "test_photos"])
# subprocess.run(["zip", "-r", "results/rez.zip",  "test_photos"])
