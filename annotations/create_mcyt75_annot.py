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
def create_mcyt_annots(
    superdatabase_coco_annots_file: str,
    output_annots_file: str,
) -> None:
    """Split CEDAR database annots.
    Args:
        superdatabase_coco_annots_file:
            Json file in COCO format with annotations of superdatabase
        output_annots_file:
            File where COCO annotation will be saved for CEDAR database.
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

        if 'MCYT-' in cat["name"]:
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

    coco_annots["categories"] = categories
    coco_annots["images"] = images

    logger.info(f"Writing {output_annots_file}...")
    with open(output_annots_file, "w") as f:
        json.dump(coco_annots, f, indent=2)
    logger.info("Done!")


if __name__ == "__main__":
    fire.Fire(create_mcyt_annots)
    #example: python annotations/create_mcyt_annots.py annotations/coco_annots.json annotations/mcyt_annots.json