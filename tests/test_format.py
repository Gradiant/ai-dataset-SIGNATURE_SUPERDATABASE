import json
from pathlib import Path

import pytest
from annotations.SCHEMA import COCOClassificationDataset

ANNOTATION_FILE = str(
    Path(__file__).parent.parent / "annotations" / "SIGNATURE_SUPERDATABASE.json"
)


@pytest.mark.skipif(not Path(ANNOTATION_FILE).exists(), reason="No access to DVC cache")
def test_coco_format():
    dataset = COCOClassificationDataset(**json.load(open(ANNOTATION_FILE)))

    image_ids = [x.id for x in dataset.images]
    image_ids_set = set(image_ids)
    # No repeated ids
    assert len(image_ids) == len(image_ids_set)

    categories = [x.id for x in dataset.categories]
    categories_set = set(categories)
    # No repeated categories
    assert len(categories) == len(categories_set)

    for image in dataset.images:
        assert image.category_id in categories_set
