#%%
import numpy as np
from skimage import exposure, filters, transform, img_as_ubyte
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import hyperspy.api as hs
import argparse


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



    Args:
        emd_file (Path_object): The path of the emd file

    Returns:
        hyperspy.signal: The image object handled by hyperspy.
    """

    print(f"Converting \"{emd_file.name}\"")
    # Read image data from file:
    emd_obj = hs.load(emd_file)

    # ensure that there are no negative values in the image data (otherwise converstion to uint might be problematic):
    img = emd_obj.data
    # assert (img >= 0).all()

    # Change dtype:
    dtype="uint16"
    print("Changing dtype from", emd_obj.data.dtype, end=" ")
    emd_obj.change_dtype(dtype)
    print("to", emd_obj.data.dtype)

    save_dest = emd_file.parent / Path(f"{emd_file.stem}.tiff")
    print(f"Saving converted image to \"{save_dest.name}\"")
    emd_obj.save(save_dest, overwrite=True)

    return emd_obj


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