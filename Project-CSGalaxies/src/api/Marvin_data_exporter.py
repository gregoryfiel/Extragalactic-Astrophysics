import os
import logging
import json
from MarvinClient import Marvin

class MarvinDataExporter():
    def __init__(self, source=Marvin()):
        self.marvin = source
        self.base_output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'landing')
        os.makedirs(self.base_output_dir, exist_ok=True)

    def fetch_and_store(self, map_list):
        """Faz solicitações para uma lista de mapas e armazena os dados em JSON."""
        for map_name, bintype, template, property_name, channel in map_list:
            logging.info(f"Fetching data for {map_name}, {bintype}, {template}, {property_name}, {channel}")
            data = self.marvin.get_api(map_name, bintype, template, property_name, channel)
            self.store_to_json(map_name, property_name, channel, data)

    def store_to_json(self, map_name, property_name, channel, data):
        """Armazena a saída da API em um arquivo JSON dentro de uma pasta nomeada dinamicamente."""
        map_dir = os.path.join(self.base_output_dir, map_name)
        os.makedirs(map_dir, exist_ok=True)
        output_file = os.path.join(map_dir, f"{map_name}-{property_name}_{channel}.json")

        with open(output_file, mode='w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':

    map_list = [
        ('12772-12705', 'SPX', 'MILESHC-MASTARSSP', 'emline_gflux', 'ha_6564'),
        ('12772-12705', 'SPX', 'MILESHC-MASTARSSP', 'emline_gflux', 'hb_4862'),
        ('12772-12705', 'SPX', 'MILESHC-MASTARSSP', 'emline_gvel', 'ha_6564'),
        ('12772-12705', 'SPX', 'MILESHC-MASTARSSP', 'emline_gsigma', 'ha_6564'),
        ('12772-12705', 'SPX', 'MILESHC-MASTARSSP', 'emline_gew', 'ha_6564'),
        ('12772-12705', 'SPX', 'MILESHC-MASTARSSP', 'emline_gew', 'hb_4862'),
    ]

    marvin_exporter = MarvinDataExporter()
    marvin_exporter.fetch_and_store(map_list)
