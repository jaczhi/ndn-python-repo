import asyncio
import logging
from pyndn import Face, Name
from pyndn.security import KeyChain
from repo import Repo
from handle import ReadHandle, WriteCommandHandle, DeleteCommandHandle
from storage import MongoDBStorage
from config import get_yaml


def main():

    async def face_loop():
        nonlocal face, repo
        while repo.running:
            face.processEvents()
            await asyncio.sleep(0.01)

    logging.basicConfig(format='[%(asctime)s]%(levelname)s:%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    config = get_yaml()
    print(config)

    face = Face()
    keychain = KeyChain()
    face.setCommandSigningInfo(keychain, keychain.getDefaultCertificateName())
    storage = MongoDBStorage(config['db_config']['mongodb']['db'],
                             config['db_config']['mongodb']['collection'])

    read_handle = ReadHandle(face, keychain, storage)
    write_handle = WriteCommandHandle(face, keychain, storage, read_handle)
    delete_handle = DeleteCommandHandle(face, keychain, storage)

    repo = Repo(Name(config['repo_config']['repo_name']),
                face, storage, read_handle, write_handle, delete_handle)

    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(face_loop())
    finally:
        event_loop.close()


if __name__ == "__main__":
    main()

