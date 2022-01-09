from fastapi import UploadFile
import aiofiles
import secrets


async def save_file(file: UploadFile) -> str:
    filename = "static/" + secrets.token_hex(nbytes=16)+file.filename

    async with aiofiles.open(filename, 'wb') as out_file:
        await out_file.write(await file.read())

    return filename
