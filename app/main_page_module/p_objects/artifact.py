from app.pylavor import Pylavor
import glob
import os
import itertools
from PIL import Image
from os.path import exists
import datetime
from flask import url_for, session

import random
import string

from app import app



class Artifact:
    database_name = "database.json"
    
    col_ref_num = None
    name = None
    type_  = None
    period = None
    state_entity = None
    replica = None
    provenance_notes = None
    owners = None
    description = None
    historical_context = None
    buy_price = None
    sold_price = None
    joined_collection_in_year = None
    left_collection_in_year = None
    reference = None
    public = 0
    curr_location_of_item = ""

    # coin only data
    coin_type = None
    coin_description = None
    ruler = None
    mint_city = None
    mint_period = None
    material = None
    weight = None
    diameter = None
    obverse = None
    reverse = None
    grade = None
    
    image_suffix = ".png"
    image_location = "static/artifacts/images/"

    
    def __init__(self, art_data) -> None:
        self.col_ref_num = art_data["col_ref_num"]
        self.name = art_data["name"]
        self.type_ = art_data["type_"]
        self.period = art_data["period"]
        self.state_entity = art_data["state_entity"]
        self.replica = art_data["replica"]
        self.provenance_notes = art_data["provenance_notes"]
        self.owners = art_data["owners"]
        self.description = art_data["description"]
        self.historical_context = art_data["historical_context"]
        self.buy_price = art_data["buy_price"]
        self.sold_price = art_data["sold_price"]
        self.joined_collection_in_year = art_data["joined_collection_in_year"]
        self.left_collection_in_year = art_data["left_collection_in_year"]
        self.reference = art_data["reference"]
        self.public = art_data["public"]
        self.curr_location_of_item = art_data["curr_location_of_item"]
        self.left_collection_in_year = art_data["left_collection_in_year"]
        self.coin_type = art_data["coin_type"]
        self.coin_description = art_data["coin_description"]
        self.ruler = art_data["ruler"]
        self.mint_city = art_data["mint_city"]
        self.mint_period = art_data["mint_period"]
        self.material = art_data["material"]
        self.weight = art_data["weight"]
        self.diameter = art_data["diameter"]
        self.obverse = art_data["obverse"]
        self.reverse = art_data["reverse"]
        self.grade = art_data["grade"]
    
    # Artifact
    @staticmethod
    def check_db_existing():
        exists = Pylavor.check_file_exists(f"data/{Artifact.database_name}")
        
        if not exists:
            Pylavor.create_folder("data")
            Pylavor.json_write("data", Artifact.database_name, {}, sanitation=False)
            
        

    # Artifact
    @staticmethod
    def col_ref_num_new(type_):
        all_artifacts = Pylavor.json_read("data", Artifact.database_name)
        
        max_num = 0
        
        for col_ref_num, _ in all_artifacts.items():
            print(col_ref_num.split("_"))
            new_num = int(col_ref_num.split("_")[1])
            
            if new_num >= max_num:
                max_num = new_num
        
        max_num = max_num + 1
        col_ref_num = f"{type_[:2]}_{max_num}"
        
        return col_ref_num
    
    def save(self):
        all_artifacts = Pylavor.json_read("data", Artifact.database_name)

        all_artifacts[self.col_ref_num] = self.to_json()
        
        Pylavor.json_write("data", Artifact.database_name, all_artifacts)    
    
    # Artifact
    @staticmethod
    def get_one(col_ref_num):
        all_artifacts = Pylavor.json_read("data", Artifact.database_name)

        if col_ref_num not in all_artifacts:
            return False

        return all_artifacts[col_ref_num]

    # Artifact
    @staticmethod
    def get_all(type_, limit=0, random_=False):
        Artifact.check_db_existing()
     
        all_artifacts = Pylavor.json_read("data", Artifact.database_name)
        
        if not session.get('user_id'):
            all_artifacts = {k: v for k, v in all_artifacts.items() if v["public"] != "0"}
        
        if type_ != "all":
            if type_.startswith("not_"):
                type_ = type_[4:]
                all_artifacts = {k: v for k, v in all_artifacts.items() if v["type_"] != type_}
            else:
                all_artifacts = {k: v for k, v in all_artifacts.items() if v["type_"] == type_}
        
        if not random_:
            sorted_artifacts = dict(sorted(all_artifacts.items(), key=lambda item: item[1]["joined_collection_in_year"], reverse=True))
        else:
            items = list(all_artifacts.items())
            random.shuffle(items)
            sorted_artifacts = dict(items)
            
            
        if limit != 0:
            return dict(itertools.islice(sorted_artifacts.items(), limit))
        else:
            return sorted_artifacts
    

    def to_json(self):
        data_ = {"col_ref_num": self.col_ref_num,
                 "name": self.name,
                 "type_": self.type_,
                 "period": self.period,
                 "state_entity": self.state_entity,
                 "replica": self.replica,
                 "provenance_notes": self.provenance_notes,
                 "owners": self.owners,
                 "description": self.description,
                 "historical_context": self.historical_context,
                 "buy_price": self.buy_price,
                 "sold_price": self.sold_price,
                 "joined_collection_in_year": self.joined_collection_in_year,
                 "left_collection_in_year": self.left_collection_in_year,
                 "reference": self.reference,
                 "public": self.public,
                 "curr_location_of_item": self.curr_location_of_item,
                 "left_collection_in_year": self.left_collection_in_year,
                 "coin_type": self.coin_type,
                 "coin_description": self.coin_description,
                 "ruler": self.ruler,
                 "mint_city": self.mint_city,
                 "mint_period": self.mint_period,
                 "material": self.material,
                 "weight": self.weight,
                 "diameter": self.diameter,
                 "obverse": self.obverse,
                 "reverse": self.reverse,
                 "grade": self.grade
            }

        return data_
    
    # Artifact
    @staticmethod    
    def generate_random_filename(col_ref_num, ext=".png"):
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return f"{col_ref_num}_{random_part}{ext}"    
    
    # Artifact
    def remove_trasparency(self, im, bg_colour=(255, 255, 255)):
        # Only process if image has transparency (http://stackoverflow.com/a/1963146)
        if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
    
            # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
            alpha = im.convert('RGBA').getchannel('A')
    
            # Create a new background image of our matt color.
            # Must be RGBA because paste requires both images have the same format
            # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
            bg = Image.new("RGBA", im.size, bg_colour + (255,))
            bg.paste(im, mask=alpha)
            return bg
    
        else:
            return im        
    
    # Artifact
    def write_image(self, image_data):
        _, number_of_them = self.get_images()
        new_filename = os.path.join(app.root_path, self.image_location, 
                                    self.generate_random_filename(self.col_ref_num))
        
        with Image.open(image_data) as photo:
            #photo = photo.resize((500,500))
            photo = self.remove_trasparency(photo)
            
            MAX_SIZE = (1500, 1500)
            photo.thumbnail(MAX_SIZE)
            
            photo.save(new_filename, format="png")    
    
    # Artifact
    def delete_image(self, image_name):
        new_filename = os.path.join(app.root_path, self.image_location, image_name)        
        print(new_filename)
        if os.path.exists(new_filename):
            os.remove(new_filename)
            print("deleted")

    
    # Artifact
    @staticmethod
    def yes_no(yes_no):
        if yes_no == 1 or yes_no == "1" or yes_no == True:
            return "Da"
        else:
            return "Ne"
    # Artifact
    @staticmethod
    def types(type_=False):
        types_ = {
            "Kovanec": "coin",
            "Bodala in Meči": "bladed",
            "Vojaški Predmeti": "military_artifacts",
            "Odlikovanja": "medals",
            "Starine": "artifacts"
            
        }
        
        if type_ != False:
            return next((k for k, v in types_.items() if v == type_), None)        

        return types_
    
    # Artifact
    @staticmethod
    def periods(period=False):
        periods_ = {
            "Predzgodovina": ["prehistory", "~2.5 million years ago - ~3,000 BC"],
            "Bronasta Doba": ["bronze_age", "~3,300 BC – ~1,200 BC"],
            "Železna Doba": ["iron_age", "~1,200 BCE – ~8th BC"],
            "Klasična Antika": ["classical_antiquity", "~8th BC - ~5th AD"],
            "Srednji Vek": ["middle_age", "~5th AD - ~16th AD"],
            "Renesansa": ["renaissance", "~14th AD – ~17th AD"],
            "Doba Odkritij": ["age_of_discovery", "~16th AD – ~18th AD"],
            "Sodobna Doba": ["modern_period", "~18th AD - Danes"],
            "WW1": ["ww1", "1914 - 1918"],
            "WW2": ["ww2", "1939 - 1945"]
        }
        
        if period != False:
            return next((k for k, v in periods_.items() if v[0] == period), None)
        return periods_
    
    
    # Artifact
    @staticmethod
    def grades(grade = False):
        grades_ = {
            "Good": "G",
            "Very Good": "VG",
            "Fine": "F",
            "Very Fine": "VF",
            "Extremely Fine": "XF",
            "About Uncirculated": "AU",
            "Uncirculated": "UNC"
            
        }
        
        if grade != False:
            return next((k for k, v in grades_.items() if v == grade), None)
        return grades_   
    
    # Artifact
    def get_images(self):
        location = os.path.join(app.root_path, self.image_location)
        matching_files = glob.glob(os.path.join(location, f"{self.col_ref_num}*"))
        
        file_names = [os.path.basename(f) for f in matching_files]
        
        return file_names, len(matching_files)

        