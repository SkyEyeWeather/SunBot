# =========================================#
#           SUN IMAGE CLASS               #
# _________________________________________#
# Author :  Clément PAGES                 #
# Version : 1.0                           #
# =========================================#

# =======================================#
#       MODULE USED BY THIS CLASS       #
# =======================================#

import logging

from PIL import Image as img
from PIL import ImageDraw
from PIL import ImageFont as font
from PIL import UnidentifiedImageError

# ===============================#
#       CLASS DEFINITION        #
# ===============================#


class SunImage:
    """This class provides methods to generate an image. An image is composed of a background image
    and elements added on top of it, such as other images, or text elements"""

    def __init__(
        self, background_img: str, width: int = 1050, height: int = 700
    ) -> None:
        """Creates an image from the image pointed by the specified path. Loaded image is resized
        according to optional `width` and `height `arguments. If these parameters is not set, image
        is not resized and keep its original dimensions.
        ## Parameters:
        * `background_img` : string representing path to the image to load
        * `width` : optional. If specified, new width for the loaded image
        * `height` : optional. If specified, new height for the loaded image
        ## Return value:
        not applicable
        ##Exceptions:
        * `ValueError` : if specified width or height have negative value"""
        if width < 0 or height < 0:
            raise ValueError(
                f"Width or height must have positive value. Given value w = {width}, h = {height}"
            )
        # Try to load the specified image. If it does not exist, create a new image with
        # black background and default size:
        try:
            logging.info("Loading image from %s...", background_img)
            self.background_img = img.open(background_img)
            self.background_img = self.background_img.resize((width, height))
        except (FileNotFoundError, UnidentifiedImageError):
            logging.error(
                "Image at %s cannot be found. Please check the path", background_img
            )
            logging.info("Creating a default image with black background")
            self.background_img = img.new("RGBA", (width, height))

        self.draw_tool = ImageDraw.ImageDraw(self.background_img)
        self.height = self.background_img.height
        self.width = self.background_img.width

    # Getters and setters:
    def get_img_size(self) -> tuple:
        """Returns this image size as a tuple
        ## Parameters:
        not applicable
        ## Return value:
        Image dimensions, as a tuple (`width`, `height`)"""
        return self.background_img.size

    def resize_img(self, width: int, height: int) -> None:
        """Resizes this image according to specified `width` and `height`
        ## Parameters:
        * `width`: new width for this image
        * `height`: new height for this image
        ## Return value: not applicable"""
        self.background_img.resize((width, height))
        logging.info("Image %s", self.background_img.__str__)

    def add_mask(
        self,
        color: str,
        alpha: int,
        size: tuple,
        position: tuple,
        rotation: float = 0.0,
    ) -> None:
        """Adds a new mask to this image, with specified `maskColor` and `alpha` value.
        ## Parameters:
        * `color`: color of the mask to be generated
        * `alpha`: alpha value for the mask to be generated
        * `size`:  size of the mask to be generated as a tuple, with firstly width and then height
        * `position`: coordinates where place the mask on the image, as a tuple
        * `rotation` : angle rotation for the mask, optional
        ## Return value: not applicable
        ## Exceptions:
        * `ValueError`: if one of the specified argument has an incorrect value"""
        # Arguments checks :
        if alpha < 0 or alpha > 255:
            logging.error(
                "Specified value for the argument 'alpha' %d is not correct", alpha
            )
            raise ValueError(
                f"Alpha argument must be in 0-255 range. Given value : {alpha}"
            )
        if len(size) != 2 or size[0] < 0 or size[1] < 0:
            logging.error(
                "Tuple size must have a len of 2 : (width, height). Current size: %d",
                len(size)
            )
            raise ValueError("addMask : tuple specified for mask size is incorrect.")
        if len(position) != 2 or position[0] < 0 or position[1] < 0:
            logging.error("Specified value for width and height must be positive")
            raise ValueError(
                "addMask : tuple specified for mask position is incorrect."
            )

        # Creation of the mask :
        mask = img.new("RGBA", size, color)
        mask.putalpha(alpha)
        mask = mask.rotate(rotation)

        # Add mask to this image :
        self.background_img.paste(mask, position, mask)

    def add_icon(
        self, icon: str, size: tuple, position: tuple, rotation: float = 0.0
    ) -> None:
        """Adds the icon pointed by the specified path to this image, with the given size,
        position and rotation angle.
        ## Parameters:
        * `icon`: path to the icon to add on this image, as a string
        * `size`: icon size on this image, as a tuple (width, height)
        * `position`: position where to place the icon on this image, as a tuple (x, y)
        * `rotation` : rotation angle for the icon on this image, optional
        ## Return value: not applicable
        ## Exceptions:
        * `ValueError`: if one of the specified argument has an incorrect value"""
        # Arguments checks :
        if len(size) != 2 or size[0] < 0 or size[1] < 0:
            logging.error(
                "Tuple size for icon size must have a len of 2 : (width, height). Current size: %d",
                len(size)
            )
            raise ValueError("addIcon : tuple specified for icon size is incorrect.")
        if len(position) != 2 or position[0] < 0 or position[1] < 0:
            logging.error(
                "Tuple size for icon position must have a len of 2: "
                "(width, height). Current size: %s",
                len(position)
            )
            raise ValueError(
                "addIcon : tuple specified for icon position is incorrect."
            )
        # Try to load and resize the specified icon:
        try:
            icon = img.open(icon).convert("RGBA")
            icon = icon.resize(size).rotate(rotation)
        except (FileNotFoundError, UnidentifiedImageError):
            logging.error(
                "Specified icon at %s doesn't exist. Please check the icon path."
                "Icon can't be added to this image",
                icon
            )
        else:
            # Add the icon to the image :
            self.background_img.paste(icon, position, icon)

    def draw_txt(
        self, text: str, txt_font: font.ImageFont, position: tuple, color="WHITE"
    ) -> None:
        """Writes specified `text` on this image, with the given font and color
        and at the specified position on the image
        ## Parameters:
        * `text` : text to write on this image
        * `txt_font` : font used to write the text on this image
        * `position` : position where to write the text on this image, as a tuple (x, y)
        * `color` : optional, color of the text to write, default color is white
        ## Return value: not applicable
        ## Exceptions:
        * `ValueError`: if one of the specified argument has an incorrect value"""
        # Arguments checks :
        if len(position) != 2 or position[0] < 0 or position[1] < 0:
            logging.error(
                "Tuple size for icon position must have a len of 2 : (width, height)."
                "Current size: %d",
                len(position),
            )
            raise ValueError(
                "addMask : tuple specified for mask position is incorrect."
            )
        if txt_font is None:
            raise ValueError("drawText : Font must be defined")

        # Write the text on this image :
        self.draw_tool.text(position, text, color, font=txt_font)

    def save_img(self, save_location: str, img_format: str = "png") -> None:
        """Saves this image at the specified `saveLocationPath` and `img_format`
        ## Parameters:
        * `save_location`: path where to save this image, as a string
        * `img_format`: optional, save format for this image, default is png
        ## Return value: not applicable
        ##Exceptions:
        * `ValueError`: if specified `format` could not be determined
        * `IOError`: if the file where save this image cannot be created
        """
        self.background_img.save(save_location, img_format)
