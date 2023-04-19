#%%
import numpy as np
from skimage import exposure, img_as_int
from skimage import io
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import hyperspy.api as hs
import argparse
import matplotlib.pyplot as plt

#%%
# Function definitions: 
def get_pixel_size(emd_obj)->float:
    """Convenience function for getting the pixel size form the MASSIVE metadata tree from hyperspys signal objects.
    Careful: In the metadata tree all values are save as string. Therefore converting to float.

    Args:
        emd_obj (hyperspy signal datatype): The data loaded form an .emd file via hyperspy

    Returns:
        float: the px size in meter
    """

    px_height = float(emd_obj.original_metadata.BinaryResult.PixelSize.height)
    px_width = float(emd_obj.original_metadata.BinaryResult.PixelSize.width)

    if px_height == px_width:
        px_size = px_height
    else:
        px_size = (px_height, px_width)
    

    return px_size

def convert_to_tiff(emd_file):
    """Convert velox's emd file to tiff file with 16 bit depth (The velox exporter also exports to 16 bit tif).
    Using the hyperspy API (http://hyperspy.org/hyperspy-doc/current/user_guide/io.html#loading-and-saving-data) for IO.

    TODO: Weird behaviour for Atlas and Square images.

    Args:
        emd_file (Path_object): The path of the emd file

    Returns:
        hyperspy.signal: The image object handled by hyperspy.
    """

    print(f"Converting \"{emd_file.name}\"")
    # Read image data from file:
    try:
        emd_obj = hs.load(emd_file)
    except OSError:
        print("Some weird hyperspy related error")
        return None    

    img = emd_obj.data
    print(f"Negative values in image: {(img < 0).any()}")
    print(f"Numpy array data type: {img.dtype}")
    print(img.min(), img.max())


    # img = img_as_int(img)

    print(f"Numpy array data type: {img.dtype}")
    print(img.min(), img.max())

    # plt.figure()
    # plt.title(f"{emd_file.name}")
    # plt.imshow(img, cmap="gray")
    # plt.show()



    save_dest = emd_file.parent / Path(f"{emd_file.stem}.tiff")
    print(f"Saving converted image to \"{save_dest.name}\"")
    
    io.imsave(save_dest, img)



##################################################################################################

parser = argparse.ArgumentParser(
    description="Command line EMD to TIFF converter"
)

parser.add_argument("emd_dir")
parser.add_argument("wildcard")

args = parser.parse_args()
emd_dir = Path(args.emd_dir)
assert emd_dir.exists() and emd_dir.is_dir()
wildcard = args.wildcard


for emd_file in emd_dir.rglob(wildcard):
    print(emd_file)
    convert_to_tiff(emd_file)