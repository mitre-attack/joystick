import copy
import os
import ntpath
from pandas.io.json import json_normalize
from app.utility.base_svc import BaseService


class DataService(BaseService):
    adversary_path = os.path.abspath('data/evaluations/')
    procedures_path = os.path.abspath('data/procedures/')
    apt29_categories = ['None', 'Telemetry', 'MSSP', 'General', 'Tactic', 'Technique', 'N/A']
    apt29_modifiers = {"None", "Alert", "Correlated", "Delayed (Manual)", "Delayed (Processing)", "Host Interrogation",
                       "Residual Artifact",
                       "Configuration Change (Detections)",
                       "Configuration Change (UX)", "Innovative"}

    mod_organized = {'datasets': {"None": [], "Alert": [], "Correlated": [],
                     "Delayed (Manual)": [], "Delayed (Processing)": [], "Host Interrogation": [],
                                  "Residual Artifact": [], "Configuration Change (Detections)": [],
                                  "Configuration Change (UX)": [], "Innovative": []}, 'labels': []}
    organized = {'datasets': {'None': [], 'Telemetry': [], 'General': [], 'Tactic': [], 'Technique': [], 'MSSP': [], 'N/A': []},
                 'labels': []}

    def __init__(self):
        self.log = self.add_service('data_svc', self)
        self.schema = dict(procedures=[], evaluations={})
        self.ram = copy.deepcopy(self.schema)

    async def load_evaluations(self):
        evaluations = await self.get_service('file_svc').get_json_files(self.adversary_path)
        for evaluation in evaluations:
            results = await self.get_service('file_svc').load_json_file(evaluation)
            name = ntpath.basename(evaluation).rstrip('.json')
            data = await self.analyze_evaluations(results, name)
            self.ram['evaluations'].update({name: {'data': data, 'results': results}})

    async def load_procedures(self):
        procedures = await self.get_service('file_svc').get_json_files(self.procedures_path)
        for procedure in procedures:
            data = await self.get_service('file_svc').load_json_file(procedure)
            name = ntpath.basename(procedure)
            self.ram['procedures'].append({name: data})

    async def get_evaluations(self):
        return self.ram.get('evaluations')

    async def get_procedures(self):
        return self.ram.get('procedures')

    async def get_evaluations(self, criteria):
        evaluations = list(self.ram['evaluations'].keys())
        evaluations = [(eval_id, eval_id.split('.')[0]) for eval_id in evaluations if criteria['round'] in eval_id]
        return sorted(evaluations)

    async def analyze_evaluations(self, results, eval_name):
        detections = 'DetectionCategories' if 'apt3' in eval_name else 'Detections'
        tmp = json_normalize(data=results['Techniques'],
                             record_path=['Steps', detections],
                             meta=['TechniqueId', 'TechniqueName', 'Tactics', ['Steps', 'SubStep']])

        tmp['Tactic'] = tmp.apply(lambda r: r.Tactics[0]['TacticName'], axis=1)
        mod_df = tmp.explode('Modifiers')
        mod_df['Step'] = mod_df.apply(lambda row: row['Steps.SubStep'].split('.', 1)[0], axis=1)
        modifier_detections = mod_df.groupby(['DetectionType', 'Modifiers']).size().to_dict()
        data = dict(modifier_detections=await self.consolidate(modifier_detections))
        data['technique'] = await self.consolidate(mod_df.groupby(['TechniqueName', 'DetectionType']).size().to_dict())
        data['total'] = tmp.groupby('DetectionType').count()['DetectionNote'].to_dict()
        data['technique_mod'] = await self.consolidate(mod_df.groupby(['TechniqueName', 'Modifiers']).size().to_dict())
        data['substep'] = await self.consolidate(mod_df.groupby(['Steps.SubStep', 'DetectionType']).size().to_dict())
        data['step'] = await self.consolidate(mod_df.groupby(['Step', 'DetectionType']).size().to_dict())
        data['tactic'] = await self.consolidate(mod_df.groupby(['Tactic', 'DetectionType']).size().to_dict())
        data['tactic_steps'] = await self.consolidate(mod_df.groupby(['Tactic', 'Step', 'DetectionType']).size().to_dict())
        data['step_modifiers'] = await self.consolidate(
            mod_df.groupby(['Step', 'Modifiers']).size().to_dict())
        return data

    async def get_data(self, criteria):
        eval_name = criteria['eval']
        if 'category' in criteria.keys():
            return self.ram['evaluations'][eval_name]['data'][criteria['data']][criteria['category']]
        else:
            return self.ram['evaluations'][eval_name]['data'][criteria['data']]

    @staticmethod
    async def consolidate(expanded_data):
        data = {}
        for tp, val in expanded_data.items():
            if tp[0] in data.keys():
                data[tp[0]].update({tp[1]: val})
            else:
                data.update({tp[0]: {tp[1]: val}})
        return data

    async def step_data(self, criteria):
        eval_name = criteria['eval']
        data = self.ram['evaluations'][eval_name]['data'][criteria['data']]
        tmp_org = copy.deepcopy(self.organized)
        for key in range(1, 21):
            key = str(key)
            tmp_org['labels'].append(key)
            for cat in self.apt29_categories:
                if cat not in data[key].keys():
                    tmp_org['datasets'][cat].append(0)
                else:
                    tmp_org['datasets'][cat].append(data[key][cat])
        return tmp_org

    async def substep_data(self, criteria):
        eval_name = criteria['eval']
        data = self.ram['evaluations'][eval_name]['data'][criteria['data']]
        tmp_org = copy.deepcopy(self.organized)
        tmp = sorted(data.items(), key=lambda k: int(k[0].split('.')[0]))
        for key in tmp:
            tmp_org['labels'].append(key[0])
            for cat in self.apt29_categories:
                if cat not in data[key[0]].keys():
                    tmp_org['datasets'][cat].append(0)
                else:
                    tmp_org['datasets'][cat].append(data[key[0]][cat])
        return tmp_org

    async def modifier_data(self, criteria):
        eval_name = criteria['eval']
        data = self.ram['evaluations'][eval_name]['data'][criteria['data']]
        tmp_org = copy.deepcopy(self.organized)
        del tmp_org['datasets']['N/A']
        apt29_cat = copy.deepcopy(self.apt29_categories)
        for key in apt29_cat[:6]:
            if key in data.keys():
                for mod in self.apt29_modifiers:
                    if mod not in data[key].keys():
                        tmp_org['datasets'][key].append(0)
                    else:
                        tmp_org['datasets'][key].append(data[key][mod])
            else:
                for mod in self.apt29_modifiers:
                    tmp_org['datasets'][key].append(0)
        return tmp_org

    async def tactic_data(self, criteria):
        eval_name = criteria['eval']
        data = self.ram['evaluations'][eval_name]['data'][criteria['data']]
        return data




