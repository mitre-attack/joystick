import os
from tinydb import TinyDB, Query
import json


class DataService:

    def __init__(self):
        self.adversary_path = os.path.abspath('data/adversaries/')
        self.procedures_path = os.path.abspath('data/procedures/')
        self.db = None
        self.check_database()
        self.Technique = Query()
        self.Step = Query()
        self.Category = Query()
        self.Screenshot = Query()

    def check_database(self):
        if os.path.isfile(os.path.join('database', 'joystick.json')):
            self.db = TinyDB('database/joystick.json')

    async def insert_data(self):
        self.db = TinyDB('database/joystick.json')
        adversary_files = await self._get_json_files(self.adversary_path)
        procedure_files = await self._get_json_files(self.procedures_path)
        await self.insert_files(adversary_files, 'Techniques')
        await self.insert_files(procedure_files, 'Steps')

    async def insert_files(self, files, key):
        if key == 'Techniques':
            await self.insert_evaluations(files)
        else:
            await self.insert_procedures(files)

    async def insert_evaluations(self, files):
        for file in files:
            base = os.path.basename(file)
            data = base.split('.')
            table = data[0] + '_' + data[2]
            await self.write_table(table, file, 'Techniques')

    async def insert_procedures(self, files):
        for file in files:
            await self.write_table(os.path.basename(file).rstrip('.json'), file, 'Steps')

    async def write_table(self, db_table, file, key):
        db_table = self.db.table(db_table)
        with open(file, encoding='utf=8') as f:
            tmp = json.load(f)
            for document in tmp[key]:
                db_table.insert(document)

    async def get_tables(self):
        tables = [table for table in self.db.tables()]
        tables.remove('_default')
        return tables

    @staticmethod
    async def _get_json_files(path):
        return [os.path.join(dp, f) for dp, dn, filenames in os.walk(path)
                for f in filenames if os.path.splitext(f)[1] == '.json']

    async def find_category(self, table, category):
        cat = self.db.table(table)
        data = cat.search(self.Technique.Steps.any(self.Step.DetectionCategories.any(self.Category.Category == category)))
        return data

    async def get_raw_eval_data(self, table):
        eval_table = self.db.table(table)
        return eval_table.all()

    @staticmethod
    async def get_eval_counts_2(data):
        none, telemetry, general, tactic, technique, mssp = {'count': []}, {'count': []}, {'count': []}, {'count': []}, \
                                                            {'count': []}, {'count': []}
        for step in data:
            none['count'].append(data[step]['None']['count'])
            telemetry['count'].append(data[step]['Telemetry']['count'])
            general['count'].append(data[step]['General']['count'])
            tactic['count'].append(data[step]['Tactic']['count'])
            technique['count'].append(data[step]['Technique']['count'])
            mssp['count'].append(data[step]['MSSP']['count'])
        return dict(none=none, telemetry=telemetry, general=general, tactic=tactic, technique=technique, mssp=mssp)

    @staticmethod
    async def get_eval_counts_1(data):
        none, telemetry, ioc, enrichment, general, specific = {'count': []}, {'count': []}, {'count': []}, {'count': []}, \
                                                            {'count': []}, {'count': []}
        for step in data:
            none['count'].append(data[step]['None']['count'])
            telemetry['count'].append(data[step]['Telemetry']['count'])
            ioc['count'].append(data[step]['Indicator of Compromise']['count'])
            enrichment['count'].append(data[step]['Enrichment']['count'])
            general['count'].append(data[step]['General Behavior']['count'])
            specific['count'].append(data[step]['Specific Behavior']['count'])
        return dict(none=none, telemetry=telemetry, general=general, ioc=ioc, specific=specific, enrichment=enrichment)

    async def get_sub_steps(self, round_id):
        table = 'APT3_OperationalFlow' if round_id == 1 else 'APT29_OperationalFlow'
        steps = self.db.table(table)
        substeps = [sub['Substep'] for sub in steps]
        return substeps

    async def get_evaluations(self):
        evals = await self.get_tables()
        evaluations = dict(APT3=[], APT29=[])
        for eval in evals:
            if "APT3" in eval:
                evaluations['APT3'].append(eval)
            else:
                evaluations['APT29'].append(eval)
        evaluations['APT3'].remove('APT3_OperationalFlow')

        tmp = dict(APT3=[], APT29=[])
        for ev in ['APT3', 'APT29']:
            for eval in evaluations[ev]:
                data = eval.split('_')
                eval_data = dict(vendor=data[0], apt=data[1])
                tmp[ev].append(eval_data)
        return tmp

    async def get_modifier_counts_2(self, table):
        data = await self.get_raw_eval_data(table)
        categories = ['None', 'Telemetry', 'General', 'Tactic', 'Technique', 'MSSP']
        tmp = dict()
        for cat in categories:
            tmp[cat] = {
                "Alert": 0,
                "Correlated": 0,
                "Delayed (Manual)": 0,
                "Delayed (Processing)": 0,
                "Host Interrogation": 0,
                "Residual Artifact": 0,
                "Configuration Change (Detections)": 0,
                "Configuration Change (UX)": 0,
                "Innovative": 0,
            }
        for tech in data:
            for step in tech['Steps']:
                for detect in step['Detections']:
                    for mod in detect['Modifiers']:
                        tmp[detect['DetectionType']][mod] += 1
        for item in tmp.keys():
            tmp[item] = [tmp[item][key] for key in tmp[item].keys()]

        return tmp

    async def get_modifier_counts_1(self, table):
        data = await self.get_raw_eval_data(table)
        categories = ['None', 'Telemetry', 'Indicator of Compromise', 'Enrichment', 'General Behavior', 'Specific Behavior']
        tmp = dict()
        for cat in categories:
            tmp[cat] = {
                "Delayed": 0,
                "Tainted": 0,
                "Configuration Change": 0,
            }
        for tech in data:
            for step in tech['Steps']:
                for detect in step['DetectionCategories']:
                    if "Modifiers" in detect.keys():
                        for mod in detect['Modifiers']:
                            tmp[detect['Category']][mod] += 1
                    else:
                        continue

        for item in tmp.keys():
            tmp[item] = [tmp[item][key] for key in tmp[item].keys()]
        return tmp

    async def get_eval_results_data_2(self, table):
        data = await self.build_data_dict_2()
        found = await self.get_raw_eval_data(table)
        for item in found:
            for step in item['Steps']:
                if step['SubStep'].split('.')[0] == '19':
                    continue
                step_num = 'Step' + str(step['SubStep'].split('.')[0])
                mod_dict = {'Alert': 0, 'Correlated': 0, 'Delayed (Manual)': 0, 'Delayed (Processing)': 0,
                            'Host Interrogation': 0,
                            'Residual Artifact': 0, 'Configuration Change (Detections)': 0,
                            'Configuration Change (UX)': 0, 'Innovative': 0}
                for cat in ['None', 'Telemetry', 'General', 'Tactic', 'Technique', 'MSSP']:
                    data[step_num][cat].update(dict(modifiers=mod_dict))
                for category in step['Detections']:
                    data[step_num][category['DetectionType']]['count'] += 1
                    for modifier in category['Modifiers']:
                        data[step_num][category['DetectionType']]['modifiers'][modifier] += 1
        return data

    async def get_eval_results_data_1(self, table):
        data = await self.build_data_dict_1()
        found = await self.get_raw_eval_data(table)
        for item in found:
            for step in item['Steps']:
                step_num = 'Step' + str(step['SubStep'].split('.')[0])
                mod_dict = {'Delayed': 0, 'Tainted': 0, 'Configuration Change': 0}
                for cat in ['None', 'Telemetry', 'Indicator of Compromise', 'Enrichment', 'General Behavior', 'Specific Behavior']:
                    data[step_num][cat].update(dict(modifiers=mod_dict))
                for category in step['DetectionCategories']:
                    data[step_num][category['Category']]['count'] += 1
                    if 'Modifiers' not in category:
                        continue
                    else:
                        for modifier in category['Modifiers']:
                            data[step_num][category['Category']]['modifiers'][modifier] += 1

        return data

    @staticmethod
    async def build_data_dict_2():
        data = dict()
        for i in range(1, 21):
            step_num = 'Step' + str(i)
            data[step_num] = {'Telemetry': dict(count=0), 'General': dict(count=0),
                              'Tactic': dict(count=0), 'Technique': dict(count=0),
                              'None': dict(count=0), 'MSSP': dict(count=0)}
        return data

    @staticmethod
    async def build_data_dict_1():
        data = dict()
        for i in range(1, 21):
            step_num = 'Step' + str(i)
            data[step_num] = {'Telemetry': dict(count=0), 'General Behavior': dict(count=0),
                              'Enrichment': dict(count=0), 'Specific Behavior': dict(count=0),
                              'None': dict(count=0), 'Indicator of Compromise': dict(count=0)}
        return data

