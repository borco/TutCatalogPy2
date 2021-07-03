from pathlib import Path
from typing import List, Set

from pytest import mark

from tutcatalogpy.common.files import get_images


@mark.parametrize(
    'files, results',
    [
        (['image1.jpg'], {'image1.jpg'}),
        (['Image1.JPG'], {'Image1.JPG'}),
        (['image01.jpg'], {'image01.jpg'}),
        (['image10.jpg'], {'image10.jpg'}),
        (['image99.jpg'], {'image99.jpg'}),
        (['image.jpg'], set()), # no number after image
        (['foo1.jpg'], set()), # doesn't start with image
        (['image100.jpg'], set()), # will not extract more than 99 images
        (['foo.txt', 'image1.jpg'], {'image1.jpg'}),
        (['foo.txt', 'bar.html', 'image1.jpg'], {'image1.jpg'}),
    ]
)
def test_get_images(tmp_path: Path, files: List[str], results: Set[str]):
    for file in files:
        (tmp_path / file).touch()

    images = get_images(tmp_path)
    assert {Path(image).name for image in images} == results
