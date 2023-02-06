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

def convert_to_8bit(img_array:np.ndarray)->np.ndarray:
    """Convert image array to 8 bit for export to png

    Args:
        img_array (np.ndarray): _description_

    Returns:
        np.ndarray: _description_
    """

    return img_as_ubyte(exposure.rescale_intensity(img_array))

def converted_px_size_and_unit(px_size_meter, img_data):
    """Convert pixel size in meter to meter, mm, µm, nm, or, pm and also return the corresponding length unit.

    Args:
        px_size (_type_): _description_
        img_data (_type_): _description_

    Returns:
        _type_: _description_
    """

    im_size_x = img_data.shape[1]
    fov_x = im_size_x * px_size_meter

    units = np.array(["m", "mm", "µm", "nm", "pm"])
    scales = np.array([1e0, 1e-3, 1e-6, 1e-9, 1e-12])

    frac = fov_x / scales

    greater_one = frac >= 1
    smaller_1000 = frac < 1e3

    scale_indicator = np.logical_and(greater_one, smaller_1000)
    assert scale_indicator.any()

    unit = units[scale_indicator][0]

    scale = scales[scale_indicator][0]

    px_size_val = px_size_meter / scale

    return px_size_val, unit

def add_scalebar(im, img_data:np.ndarray, px_size_meter:float):
    """
    Add scalebar manually without using matplotlib artists
    """

    ## Adding text not really working

    global im_size_x
    im_size_x = img_data.shape[1]
    im_size_y = img_data.shape[0]

    # convert px size from meter to e.g. nm:
    px_size_conv, unit = converted_px_size_and_unit(px_size_meter, img_data)
    fov_x = im_size_x * px_size_conv
    

    # Find a good integer length for the scalebar 
    sb_len_float = fov_x / 6 #Scalebar length is about 1/6 of FOV
    # A list of allowed lengths for the scalebar (in whatever value unit has)
    sb_lst = [0.1,0.2,0.5,1,2,5,10,20,50,100,200,500,1000,2000,5000]
    # Find the closest value in the list
    sb_len = sorted(sb_lst, key=lambda a: abs(a - sb_len_float))[0]
    sb_len_px = sb_len / px_size_conv
    sb_start_x, sb_start_y = (im_size_x / 24, im_size_y *11 / 12) #Bottom left corner from 1/12 of FOV
    sb_width = im_size_y / 100
    draw = ImageDraw.Draw(im)
    sb = (sb_start_x, sb_start_y, sb_start_x + sb_len_px, sb_start_y + sb_width)
    outline_width = round(im_size_y/500)
    if outline_width == 0:
        outline_width = 1
    draw.rectangle(sb, fill = 'white', outline = 'black', width = outline_width)
    # Add text
    text = f"{sb_len} {unit}"
    fontsize = int(im_size_x / 22)
    try: 
        font = ImageFont.truetype("arial.ttf", fontsize)
    except:
        try: 
            font = ImageFont.truetype("Helvetica.ttc", fontsize)
        except:
            font = ImageFont.load_default()
    # txt_x, txt_y = (sb_start_x * 1.2, sb_start_y + fontsize * 1.2 + sb_width)
    txt_x, txt_y = (sb_start_x, sb_start_y + sb_width)
    # Add outline to the text
    draw.text((txt_x-outline_width, txt_y-outline_width), text, font=font, fill='black')
    draw.text((txt_x+outline_width, txt_y-outline_width), text, font=font, fill='black')
    draw.text((txt_x-outline_width, txt_y+outline_width), text, font=font, fill='black')
    draw.text((txt_x+outline_width, txt_y+outline_width), text, font=font, fill='black')
    # draw the text in white color:
    draw.text((txt_x, txt_y), text, fill='white', font=font, anchor=None)

def convert_to_png(emd_file):

    # read the emd file:
    print(f"Converting {emd_file.name}")
    
    emd_obj = hs.load(emd_file)
    img_data = emd_obj.data

    px_size = get_pixel_size(emd_obj)

    # reduce noise via median filter:
    img_data = filters.median(img_data)

    img_data = convert_to_8bit(img_data)

    # downscale the image:
    downscale_factor = 0.5
    img_data = transform.rescale(img_data, scale=downscale_factor, anti_aliasing=True)
    img_data = convert_to_8bit(img_data)
    print(f"Size of image scaled by {downscale_factor}:", img_data.shape)
    px_size = px_size / downscale_factor

    # add ad scalebar and save png file:
    im = Image.fromarray(img_data)
    add_scalebar(im, img_data, px_size_meter=px_size)
    save_dest = emd_file.parent / Path(f"{emd_file.stem}.png")
    print(f"Writing png file (down-)scaled by {downscale_factor} to {save_dest.name}")
    im.save(save_dest)



##################################################################################################

parser = argparse.ArgumentParser(
    prog="Command line EMD to PNG converter"
)

parser.add_argument("emd_dir")
parser.add_argument("wildcard")

args = parser.parse_args()
emd_dir = Path(args.emd_dir)
assert emd_dir.exists() and emd_dir.is_dir()
wildcard = args.wildcard


for emd_file in emd_dir.rglob(wildcard):
    print(emd_file)
    convert_to_png(emd_file)