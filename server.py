import aiohttp_jinja2
import yaml
import asyncio
from aiohttp import web
import logging
import jinja2

from app.service.data_svc import DataService
from app.service.file_svc import FileService
from app.api.api import RestApi


def setup_logger(level=logging.DEBUG):
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(levelname)-5s (%(filename)s:%(lineno)s %(funcName)s) %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    for logger_name in logging.root.manager.loggerDict.keys():
        if logger_name in ('aiohttp.server', 'asyncio'):
            continue
        else:
            logging.getLogger(logger_name).setLevel(100)


async def init(address, port, services):
    app = web.Application()
    RestApi(app, services).enable()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    app.router.add_static('/webapp', 'static')
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, address, port).start()


def main(address, port, services):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(data_svc.load_evaluations())
    loop.run_until_complete(data_svc.load_procedures())
    loop.run_until_complete(init(address, port, services))
    try:
        logging.info('Joystick running.')
        loop.run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    setup_logger(getattr(logging, 'INFO'))
    with open('conf/config.yml') as conf:
        config = yaml.safe_load(conf)
        config_host = config['host']
        config_port = config['port']
        file_svc = FileService()
        data_svc = DataService()
        services = dict(file_svc=file_svc, data_svc=data_svc)
        main(config_host, config_port, services)


