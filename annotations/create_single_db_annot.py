import json
import re
from pathlib import Path
from typing import Optional

import fire
from loguru import logger
from PIL import Image
import os
from tqdm import tqdm

@logger.catch(reraise=True)  # noqa: C901
def create_single_db_annot(
    superdatabase_coco_annots_file: str,
    db_name: str,
    output_annots_file: str,
) -> None:
    """Split single databases annots.
    Args:
        superdatabase_coco_annots_file:
            Json file in COCO format with annotations of superdatabase
        db_name:
            Name of the single database. Possible options: CEDAR, MCYT, UTSIG, BHSIG, ICDAR09, ICDAR11 ICFHR
        output_annots_file:
            File where COCO annotation will be saved for UTSIG database.
    """

    Path(output_annots_file).parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading ids data from {superdatabase_coco_annots_file} ...")
    with open(superdatabase_coco_annots_file) as superdb_annots:
        annots = json.load(superdb_annots)

  
    coco_annots = {}
    images = []
    categories  =[]
    list_cat_ids = []

    logger.info("Split categories information....")
    count_categories = 0
    for cat in annots["categories"]:

        if db_name in cat["name"]:
            categories.append(cat)
            list_cat_ids.append(cat['id'])
            count_categories+=1
    logger.info(f'Added {count_categories} categories of {len(annots["categories"])} ')

    logger.info("Split images information...")
    count_images = 0
    for im in annots['images']:
        if im['category_id'] in list_cat_ids:
            images.append(im) 
            count_images += 1

    logger.info(f'Added {count_images} images of {len(annots["images"])}')

    categories2 = [
        {"id": 0, "name": "Genuine", "supercategory": "spoof"},
        {"id": 1, "name": "Forgery", "supercategory": "spoof"},
    ]

    coco_annots["categories"] = categories
    coco_annots["categories2"] = categories2
    
    coco_annots["images"] = images

    logger.info(f"Writing {output_annots_file}...")
    with open(output_annots_file, "w") as f:
        json.dump(coco_annots, f, indent=2)
    logger.info("Done!")
    


if __name__ == "__main__":
    fire.Fire(create_single_db_annot)
    #example: python annotations/create_single_db_annot.py annotations/coco_annots.json MCYT annotations/mcyt_annots.json