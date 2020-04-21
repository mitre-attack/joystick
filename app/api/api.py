import logging
from aiohttp import web
from aiohttp_jinja2 import template


class RestApi:

    def __init__(self, app, services):
        self.app = app
        self.data_svc = services.get('data_svc')
        self.file_svc = services.get('file_svc')
        self.log = logging.getLogger('rest_api')

    def enable(self):
        self.app.router.add_route('GET', '/', self.landing)
        self.app.router.add_route('GET', '/evaluations', self.evaluations)
        self.app.router.add_route('GET', '/about', self.about)
        self.app.router.add_route('*', '/rest', self.rest_api)

    @template('index.html')
    async def landing(self, request):
        return dict()

    @template('evaluations.html')
    async def evaluations(self, request):
        return dict()

    async def about(self, request):
        return web.Response(text='about')

    async def rest_api(self, request):
        data = dict(await request.json())
        index = data.pop('index')
        options = dict(
            POST=dict(
                get_evals=lambda d: self.data_svc.get_evaluations(criteria=d),
                get_eval_results=lambda d: self.data_svc.evaluation_results(criteria=d),
                get_data=lambda d: self.data_svc.get_data(criteria=d),
                step_data=lambda d: self.data_svc.step_data(criteria=d),
                sub_step_data=lambda d: self.data_svc.substep_data(criteria=d),
                mod_data=lambda d: self.data_svc.modifier_data(criteria=d),
                tactic_data=lambda d: self.data_svc.tactic_data(criteria=d)
            )
        )
        output = await options[request.method][index](data)
        return web.json_response(output)