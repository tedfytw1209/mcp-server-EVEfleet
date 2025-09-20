import yaml

def set_globals_from_dict(d):
    for key, value in d.items():
        globals()[key] = value
        
with open('config.yaml', 'r', encoding="utf-8") as f:
    config = yaml.safe_load(f)

CONFIG = config
