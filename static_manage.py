"""_summary_
Code for EVE API management char/location/UI
"""
#import
from pathlib import Path
import csv
import yaml

from IO.API_IO import (post_name2id, post_id2name)

#manage char name<->char id
class CharID_Dict():
    def __init__(self,
                 init_file_name='setting/chardict.yaml') -> None:
        init_file = Path(init_file_name)
        self.name2id_key = "characters"
        self.id2name_key = "character"
        if init_file.exists():
            with open(init_file) as file:
                self.char_name2id = yaml.safe_load(file)
            self.char_id2name = {v:k for k,v in self.char_name2id.items()}
        else:
            self.char_name2id = {}
            self.char_id2name = {}
        self.init_file = init_file
    #check
    def check_names(self,names_list):
        return [n for n in names_list if self.char_name2id.get(n.lower(),None)==None]
    def check_ids(self,ids_list):
        return [n for n in ids_list if self.char_id2name.get(n,None)==None]
    #update names
    def update_names(self,names_list):
        need_list = self.check_names(names_list)
        if need_list:
            data = post_name2id(need_list)
            new_name2id_dic = {e['name'].lower():int(e['id']) for e in data[self.name2id_key]}
            new_id2name_dic = {v:k for k,v in new_name2id_dic.items()}
            self.char_name2id.update(new_name2id_dic)
            self.char_id2name.update(new_id2name_dic)
            self.save()
        return [self.char_name2id[name.lower()] for name in names_list]
    #update ids
    def update_ids(self,ids_list):
        need_list = self.check_ids(ids_list)
        if need_list:
            data = post_id2name(need_list)
            new_id2name_dic = {int(e['id']):e['name'].lower() for e in data if e['category']==self.id2name_key}
            new_name2id_dic = {v:k for k,v in new_id2name_dic.items()}
            self.char_name2id.update(new_name2id_dic)
            self.char_id2name.update(new_id2name_dic)
            self.save()
        return [self.char_id2name[id] for id in ids_list]
    #call
    def __call__(self, charidorname: int|str):
        #api call if not exist in dict, not good
        if isinstance(charidorname, int):
            if charidorname not in self.char_id2name:
                self.update_ids([charidorname])
            output = self.char_id2name.get(charidorname,None)
        else:
            charidorname = charidorname.lower()
            if charidorname not in self.char_name2id:
                self.update_names([charidorname])
            output = self.char_name2id.get(charidorname,None)
        return output
    
    #save to yaml
    def save(self):
        with open(self.init_file,'w') as f:
            yaml.dump(self.char_name2id,f)

#System Dict static name<->id
class Static_Dict(CharID_Dict):
    def __init__(self,
                 init_file_name,name2id_key,id2name_key) -> None:
        init_file = Path(init_file_name)
        self.name2id_key = name2id_key
        self.id2name_key = id2name_key
        if init_file.exists():
            with open(init_file) as file:
                self.char_name2id = yaml.safe_load(file)
            self.char_id2name = {v:k for k,v in self.char_name2id.items()}
        else:
            self.char_name2id = {}
            self.char_id2name = {}
        self.init_file = init_file

#Ship Dict
class ShipID_Dict():
    def __init__(self,
                 init_file_name='setting/shipid_list.csv') -> None:
        with open(init_file_name) as csvfile:
            rows = csv.reader(csvfile)
            print('Loading ship id list from',init_file_name)
            self.update_ids(rows)
    #update ids
    def update_ids(self,csv_rows):
        self.ship_id2name, self.ship_name2id = {},{}
        col_names = []
        for row in csv_rows:
            if not col_names:
                col_names = [n for n in row]
            else:
                type_id = int(row[0])
                type_name = row[2]
                self.ship_id2name[type_id] = type_name
                self.ship_name2id[type_name] = type_id
        self.col_names = col_names
        self.ship_names = [n for n in self.ship_name2id.keys()]
        print('Updated ship id list:',len(self.ship_id2name))      
    #call
    def __call__(self, idorname: int|str):
        #api call if not exist in dict, not good
        if idorname in self.ship_id2name:
            output = self.ship_id2name.get(idorname,None)
        elif idorname in self.ship_name2id:
            output = self.ship_name2id.get(idorname,None)
        else:
            raise ValueError(f"Ship id/name '{idorname}' not found in dictionary.")
        return output
    
#Ship Dict
class ShipClass_Dict():
    def __init__(self,
                 init_file_name='setting/class2ship_list.csv') -> None:
        with open(init_file_name) as csvfile:
            rows = csv.reader(csvfile)
            print('Loading ship class list from',init_file_name)
            self.update(rows)
    #update ids
    def update(self,csv_rows):
        #id is ship_name, name is class_name
        self.ship_id2name, self.ship_name2id = {},{}
        col_names = []
        for row in csv_rows:
            if not col_names:
                col_names = [n for n in row]
            else:
                type_id = row[0]
                type_name = row[1]
                self.ship_id2name[type_id] = type_name
                self.ship_name2id[type_name] = type_id
        self.col_names = col_names
        self.ship_names = [n for n in self.ship_name2id.keys()]
        print('Updated ship id list:',len(self.ship_id2name)) 
    #call
    def __call__(self, idorname: str):
        #api call if not exist in dict, not good
        if idorname in self.ship_id2name:
            output = self.ship_id2name.get(idorname,None)
        elif idorname in self.ship_name2id:
            output = self.ship_name2id.get(idorname,None)
        else:
            raise ValueError(f"Ship class '{idorname}' not found in dictionary.")
        return output

#test main
if __name__ == '__main__':
    pass
        