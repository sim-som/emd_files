#%%
import hyperspy.api as hs
import numpy as np
import mrcfile
from pathlib import Path
from matplotlib import pyplot as plt

# %%

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

def convert_to_mrc(emd_file:Path):
    print(f"Converting {emd_file.name} to .mrc ...")
    
    #load emd file:
    emd_obj = hs.load(emd_file)
    # get image data as numpy array:
    img_array = emd_obj.data
    img_array = img_array.astype(np.uint16)
    # get px size from emd object:
    px_size = get_pixel_size(emd_obj)
    
    if isinstance(px_size, float):
        x_size = px_size
        y_size = px_size
    elif len(px_size) == 2:
        x_size = px_size[-1]
        y_size = px_size[0]

    dest_path = emd_file.parent / f"{emd_file.stem}.mrc"
    with mrcfile.new(dest_path, overwrite=True) as f:
        f.set_data(img_array)
        f._set_voxel_size(x_size=x_size, y_size=y_size, z_size=0.0)


# %%
#############################################################################

dest_dir = Path(
    "/home/simon/OneDrive/Bilder/Microscopy/Talos_L120C/2022-10-04-SULFO_DIBMA-C2/Grid_1L-SULFO_DIBIMA_C2-just_Receptor"
)

path_list = list(dest_dir.glob("*92000*.emd")) + list(dest_dir.glob("*120 k*.emd")) + list(dest_dir.glob("*57000*.emd")) + list(dest_dir.glob("*73000*.emd")) 

for emd_file in path_list:
    
    convert_to_mrc(emd_file)

# %%
