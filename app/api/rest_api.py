from aiohttp_jinja2 import template


class RestAPI:

    def __init__(self, services):
        self.results_svc = services.get('results_svc')
        self.data_svc = services.get('data_svc')

    @template('index.html')
    async def index(self, request):
        return

    @template('apt29_results.html')
    async def apt29_results(self, request):
        page = dict(vendor=request.match_info.get('vendor'))
        page['apt'] = 'APT29'
        page['evaluations'] = await self.data_svc.get_evaluations()
        table = page['vendor'] + '_' + page['apt']

        page['data'] = await self.data_svc.get_eval_results_data_2(table)
        sub_step_data = await self.sub_step_results_round_2(table)
        page['counts'] = await self.data_svc.get_eval_counts_2(page['data'])
        page['sub_step'] = await self.data_svc.get_eval_counts_2(sub_step_data)
        page['mod_counts'] = await self.data_svc.get_modifier_counts_2(table)

        return page

    @template('apt3_results.html')
    async def apt3_results(self, request):
        page = dict(vendor=request.match_info.get('vendor'))
        page['apt'] = 'APT3'
        page['evaluations'] = await self.data_svc.get_evaluations()
        table = page['vendor'] + '_' + page['apt']

        page['data'] = await self.data_svc.get_eval_results_data_1(table)
        sub_step_data = await self.sub_step_results_round_1(table)
        page['counts'] = await self.data_svc.get_eval_counts_1(page['data'])
        page['sub_step'] = await self.data_svc.get_eval_counts_1(sub_step_data)
        page['mod_counts'] = await self.data_svc.get_modifier_counts_1(table)

        return page

    async def sub_step_results_round_2(self, table):
        data = dict()
        sub_steps = await self.data_svc.get_sub_steps(2)
        for step in sub_steps:
            mod_dict = {'Alert': 0, 'Correlated': 0, 'Delayed (Manual)': 0, 'Delayed (Processing)': 0,
                        'Host Interrogation': 0,
                        'Residual Artifact': 0, 'Configuration Change (Detections)': 0,
                        'Configuration Change (UX)': 0, 'Innovative': 0}
            data[step] = {'Telemetry': dict(count=0, modifiers=mod_dict), 'General': dict(count=0, modifiers=mod_dict),
                              'Tactic': dict(count=0, modifiers=mod_dict), 'Technique': dict(count=0, modifiers=mod_dict),
                              'None': dict(count=0, modifiers=mod_dict), 'MSSP': dict(count=0, modifiers=mod_dict)}
        found = await self.data_svc.get_raw_eval_data(table)
        for item in found:
            for step in item['Steps']:
                if step['SubStep'].split('.')[0] == '19':
                    continue
                for category in step['Detections']:
                    data[step['SubStep']][category['DetectionType']]['count'] += 1
                    for modifier in category['Modifiers']:
                        data[step['SubStep']][category['DetectionType']]['modifiers'][modifier] += 1
        return data

    async def sub_step_results_round_1(self, table):
        data = dict()
        sub_steps = await self.data_svc.get_sub_steps(1)
        for step in sub_steps:
            mod_dict = {'Delayed': 0, 'Tainted': 0, 'Configuration Change': 0}
            data[step] = {'Telemetry': dict(count=0, modifiers=mod_dict), 'Indicator of Compromise': dict(count=0, modifiers=mod_dict),
                          'Specific Behavior': dict(count=0, modifiers=mod_dict), 'Enrichment': dict(count=0, modifiers=mod_dict),
                          'None': dict(count=0, modifiers=mod_dict), 'General Behavior': dict(count=0, modifiers=mod_dict)}

        found = await self.data_svc.get_raw_eval_data(table)
        for item in found:
            for step in item['Steps']:
                for category in step['DetectionCategories']:
                    data[step['SubStep']][category['Category']]['count'] += 1
                    if 'Modifiers' not in category:
                        continue
                    else:
                        for modifier in category['Modifiers']:
                            data[step['SubStep']][category['Category']]['modifiers'][modifier] += 1
        return data

    @template('vendors.html')
    async def evaluations(self, request):
        evaluations = await self.data_svc.get_evaluations()
        return dict(evaluations=evaluations)
