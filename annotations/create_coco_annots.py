import json
import re
from pathlib import Path
from typing import Optional

import fire
from loguru import logger
from PIL import Image
import os
from tqdm import tqdm


def find_category(file_name, ids_dict, db):
    id_user = -1
    name_key = []

    parse_db_rules = {
        # db_name: [name to find in file_name, name to generate key, index in split, separator in filename]
        'cedar': ["CEDAR", 'CEDAR_', 2, '_'],
        'mcyt75':["MCYT75", 'MCYT-75_', 1, '/'],
        'utsig': ["UTSig/G", 'UTSIG_', 2, '/'],
        'utsigFor': ["UTSig/Forgery", 'UTSIG_', 3, '/'],
        'bhsig': ["BHSig", 'BHSIG260_', 2, '/'],
    }

    if db in parse_db_rules:
        id_user = find_category_cedar_lmcyt75_utsig_bhsig(file_name, ids_dict, parse_db_rules[db])

    if 'icdar2009train' in db:
        id_user = find_category_icdar2009train(file_name, ids_dict)
    if 'icdar2009test' in db:
        id_user = find_category_icdar2009test(file_name, ids_dict)
    if 'icdar2011train' in db:
        id_user = find_category_icdar2011train(file_name, ids_dict)
    if 'icdar2011test' in db:
        id_user = find_category_icdar2011test(file_name, ids_dict)
    if '4nsig10' in db:
        id_user = find_category_4nsigcomp10(file_name, ids_dict)
    if '4nsig12' in db:
        id_user = find_category_4nsigcomp12(file_name, ids_dict)

    return id_user


def find_category_cedar_lmcyt75_utsig_bhsig(file_name, ids_dict, name_key):
    if name_key[0] in file_name:
        split_name = file_name.split(name_key[3])
        target = name_key[1] + str(split_name[name_key[2]])
        if target in ids_dict:
            return ids_dict[target]
    return -1

def find_category_icdar2009train(file_name, ids_dict):
    if 'icdar2009/train' in file_name:
        user_id = file_name.split('_')[1]
        target = 'ICDAR09_train_' + str(user_id)
        if target in ids_dict:
            return ids_dict[target]
    return -1

def find_category_icdar2009test(file_name, ids_dict):
    if 'icdar2009/test' in file_name:
        prefix, suffix = file_name.split('-')
        user_id = suffix[5:].split('.')[0]
        target = 'ICDAR09_test_' + str(user_id)
        if target in ids_dict:
            return ids_dict[target]
    return -1

def find_category_icdar2011train(file_name, ids_dict):
    if 'icdar2011/trainingSet' in file_name:
        preffix, suffix = file_name.split('/')[6].split('_')
        if len(preffix) > 3:
            #Is a forgery containing writer_id and user_id
            user_id = preffix[4:]
        else:
            #Is a genuine signature containing user_id (writer_id is the same)
            user_id = preffix
        target = 'ICDAR11_train_' + str(user_id) + '_' +file_name.split('/')[3]
        if target in ids_dict:
            return ids_dict[target]
    return -1

def find_category_icdar2011test(file_name, ids_dict):
    if 'icdar2011/Test' in file_name:
        preffix, suffix = file_name.split('/')[6].split('_')
        metadata, ext = suffix.split('.')
        if len(metadata) > 3:
            # Is a forgery containing writer_id and user_id
            user_id = metadata[4:]
        else:
            #Is a genuine signature containing user_id (writer_id is the same)
            user_id = metadata
        target = 'ICDAR11_test_' + str(user_id) + '_' +file_name.split('/')[3]
        if target in ids_dict:
            return ids_dict[target]
    return -1

def find_category_4nsigcomp10(file_name, ids_dict):
    if '4NSigComp2010' in file_name:
        target = 'ICFHR10_01'  if 'TrainingSet' in file_name else 'ICFHR10_02'
        if target in ids_dict:
            return ids_dict[target]
    return -1

def find_category_4nsigcomp12(file_name, ids_dict):
    if '4nSigComp2012' in file_name:
        target = 'ICFHR12_' +file_name.split('/')[3]
        if target in ids_dict:
            return ids_dict[target]
    return -1


@logger.catch(reraise=True)  # noqa: C901
def create_coco_annots(
    files_dir: str,
    ids_file: str,
    signature_names_file: str,
    output_annots_file: str,
) -> None:
    """Create annotations in COCO format for the signature superdatabase.
    Args:
        files_dir:
            Directory with the images
        ids_file:
            json file with ids for each user of the database
        signature_names_file:
            File in json format with the name of files. Names should have _g_if it is genuine or _f_ if is an attack.
        output_annots_file:
            File where COCO annotation will be saved.
    """
    Path(output_annots_file).parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading ids data from {ids_file} ...")
    with open(ids_file) as ids:
        ids_data = json.load(ids)

    logger.info(f"Loading names data from {signature_names_file} ...")
    with open(signature_names_file) as names:
        names_data = json.load(names)

    coco_annots = {}

    images = []
    categories  =[]

    logger.info("Adding categories information")
    for k,v in ids_data.items():

        entry = {}
        entry["id"] = v
        entry["name"] = k
        entry["supercategory"] = "user"
        categories.append(entry)

    coco_annots["categories"] = categories

    id = 0
    logger.info("Adding images information")

    logger.info(f'{len(names_data.items())} images will be proccesed')

    for k, v in tqdm(names_data.items()):
        #open image to get properties
        im = Image.open( os.path.join(files_dir+k))
        w, h = im.size
        entry = {}
        entry["id"] = id
        entry["width"] = w
        entry["height"] = h
        entry["file_name"]=k
        ##check the correct category
        dbs = ['cedar', 'mcyt75', 'utsig', 'utsigFor', 'bhsig', 'icdar2009train', 'icdar2009test', 'icdar2011train', 'icdar2011test', '4nsig10', '4nsig12']
        id_found = False
        for db in dbs:
            id_user = find_category(v, ids_data, db)
            if id_user >= 0:
                entry["category_id"]=id_user
                id_found = True

        entry["category_id2"] = 1 if '_f_' in k else 0

        if id_found is False:
            print(f'Error: image without category {k} and {v}')
            raise Exception(f'Error: image without category {k} and {v}')

        id += 1
        images.append(entry)

    coco_annots["images"] = images

    logger.info(f"Writing {output_annots_file}...")
    with open(output_annots_file, "w") as f:
        json.dump(coco_annots, f, indent=2)
    logger.info("Done!")


if __name__ == "__main__":
    fire.Fire(create_coco_annots)
    #example: python annotations/create_coco_annots.py /media/VA/BM_tmp/databases/signature_superdatabase/ /media/VA/BM_tmp/databases/signature_superdatabase/ids.json /media/VA/BM_tmp/databases/signature_superdatabase/signatures.json cocoannots.json