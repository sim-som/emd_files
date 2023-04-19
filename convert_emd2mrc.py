#%%
import numpy as np
from skimage import exposure, filters, transform, img_as_ubyte
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import hyperspy.api as hs
import argparse
import mrcfile


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


def convert_to_mrc(emd_file):
    """Convert velox's emd file to mrc file with 16 bit depth (The velox exporter also exports to 16 bit tif).
    Using the hyperspy API (http://hyperspy.org/hyperspy-doc/current/user_guide/io.html#loading-and-saving-data) for IO.
    As hyperspy can't write to mrc, I am using the mrcfile pyhton package for that.


    Args:
        emd_file (Path_object): The path of the emd file

    Returns:
        hyperspy.signal: The image object handled by hyperspy.
    """


    print(f"Converting {emd_file.name}")
    # Read image data from file:
    try:
        emd_obj = hs.load(emd_file)
    except OSError:
        print("Some weird hyperspy related error")
        return None

    # Change dtype:
    dtype="uint16"
    print("Changing dtype from", emd_obj.data.dtype, end=" ")
    emd_obj.change_dtype(dtype)
    print("to", emd_obj.data.dtype)

    # Get image data:
    img:np.ndarray = emd_obj.data
    # ensure that there are no negative values in the image data (otherwise converstion to uint might be problematic):
    # assert (img >= 0).all()

    # Get pixel size:
    px_size = get_pixel_size(emd_obj)

    # Write image data to mrcfrile:
    save_dest = emd_file.parent / Path(f"{emd_file.stem}.mrc")
    print(f"Saving converted image to \"{save_dest.name}\"")
    with mrcfile.new(save_dest, overwrite=True) as f:
        f.set_data(img)
        # Write pixel size (isotropic voxel size) to header (Klappt noch nicht so ganz)
        f.voxel_size = px_size

    return emd_obj

emd_obj = convert_to_mrc(Path("example_images/Grid_2Q-Abeta_control_2nd_trial 20221017 1156 92000 x.emd"))

##################################################################################################

parser = argparse.ArgumentParser(
    description="Command line EMD to MRC converter"
)

parser.add_argument("emd_dir")
parser.add_argument("wildcard")

args = parser.parse_args()
emd_dir = Path(args.emd_dir)
assert emd_dir.exists() and emd_dir.is_dir()
wildcard = args.wildcard


for emd_file in emd_dir.rglob(wildcard):
    print(emd_file)
    convert_to_mrc(emd_file)