import asyncio
import logging
import yaml
import os
from app.api.rest_api import RestAPI
from app.service.data_svc import DataService
from app.service.results_svc import ResultsService
import aiohttp_jinja2
import jinja2
from aiohttp import web


async def background_tasks():
    logging.info('Checking for joystick.json')
    if os.path.isfile(os.path.join('database', 'joystick.json')):
        pass
    else:
        logging.info('joystick.json does not exist, creating now')
        await data_svc.insert_data()


async def init(host, port):
    logging.info('server starting: %s:%s' % (host, port))
    app = web.Application()
    app.router.add_route('GET', '/', rest_api.index)
    app.router.add_route('GET', '/evaluations', rest_api.evaluations)
    app.router.add_route('GET', '/results/APT29/{vendor}', rest_api.apt29_results)
    app.router.add_route('GET', '/results/APT3/{vendor}', rest_api.apt3_results)

    app.router.add_static('/webapp/', 'webapp/static/')

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('webapp/html'))

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, host, port).start()


def main(host, port):
    loop = asyncio.get_event_loop()
    loop.create_task(background_tasks())
    loop.run_until_complete(init(host, port))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    logging.getLogger().setLevel('DEBUG')
    logging.info('Welcome to Joystick')
    with open('conf/config.yml') as c:
        config = yaml.safe_load(c)
        host = config['host']
        port = config['port']
        results_svc = ResultsService()
        data_svc = DataService()
        rest_api = RestAPI(services=dict(results_svc=results_svc, data_svc=data_svc))
        main(host, port)
