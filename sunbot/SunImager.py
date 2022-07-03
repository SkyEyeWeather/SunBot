#=========================================#
#           SUN IMAGER CLASS              #
#_________________________________________#
# Author :  Clément PAGES                 #
# Version : 1.0                           #
#=========================================#

#=======================================#
#       MODULE USED BY THIS CLASS       #
#=======================================#

from PIL import Image as img, ImageFont as font, ImageDraw


#===============================#
#       CLASS DEFINITION        #
#===============================#

class SunImager() :
    """This class provides methods to generate image and add elements on it"""

    def __init__(self, backgroundImagePath : str, width : int = -1, height : int = -1) -> None:
        """Create an image from the image pointed by the specified path. Loaded image is resize
        according to optional width and height arguments. If these parameters is not set, image
        is not resized and keep its original dimensions.
        ### Parameters :
        * backgroundImagePath [in] : string representing path to the image
        * width [in, opt] : if specified, new width for the loaded image
        * height [in, opt]": if specified, new height for the loaded image

        ### Return : not applicable"""
        if width < -1 or height < -1 :
            raise ValueError(f"Width or height must have positive value. Given value w = {width}, h = {height}")

        self.backgroundImage = img.open(backgroundImagePath)
        if width != -1:
            #resize image width :
            self.backgroundImage.resize(width, self.backgroundImage.height)
        if height != -1:
            #resize image height :
            self.backgroundImage.resize(self.backgroundImage.width, height)
        self.drawTool = ImageDraw.ImageDraw(self.backgroundImage)



    #Getters and setters:
    def getImageSize(self) -> tuple:
        """Return size of this image as tuple containing width in first position, and then image height"""
        return  self.backgroundImage.size


    def resizeImage(self, width : int, height : int) -> None:
        """Resize image according to specified width and height
        ### Parameters :
        * width [in] : new width for this image
        * height [in] : new height for this image

        ### Return : not applicable"""
        self.backgroundImage.resize((width, height))


    def addMask(self, maskColor : str, alpha : int, size : tuple, position : tuple, rotationAngle : float = 0.) -> None:
        """Add a new mask to the image, with specified maskColor and alpha value.
        ### Parameters :
        * maskColor [in] : color of the mask to be generated
        * alpha [in] : alpha value for the mask to be generated
        * size [in] :  size of the mask to be generated as a tuple, with first width and then height
        * position [in] : coordinates where place the mask to be generated as a tuple
        * rotationAngle [in, opt] : angle rotation for the mask, if specified

        ### Return : not applicable"""

        #Arguments checks :
        if alpha < 0 or alpha > 255 :
            raise ValueError(f"Alpha argument must be in 0-255 range. Given value : {alpha}")
        if len(size) != 2 or size[0] < 0 or size[1] < 0:
            raise ValueError("addMask : tuple specified for mask size is incorrect.")
        if len(position) != 2 or position[0] < 0 or position[1] < 0:
            raise ValueError("addMask : tuple specified for mask position is incorrect.")

        #Creation of the mask :
        mask = img.new("RGBA", size, maskColor)
        mask.putalpha(alpha)
        mask = mask.rotate(rotationAngle)

        #Add mask to this image :
        self.backgroundImage.paste(mask, position, mask)


    def addIcon(self, iconPath : str, size : tuple, position : tuple, rotationAngle : float = 0.) -> None:
        """Add the icon pointed by the specified path to this image, with the given size, position and
        rotation angle.
        ### Parameters :
        * iconPath [in] : path to the icon to add to the image as string
        * size [in] : icon size on the image as a tuple (width, height)
        * position [in]: position where placed icon on this image, as a tuple (x, y)
        * rotationAngle [in] : rotation angle for the icon on this image

        ### Return : not applicable"""
        #Arguments checks :
        if len(size) != 2 or size[0] < 0 or size[1] < 0:
            raise ValueError("addMask : tuple specified for mask size is incorrect.")
        if len(position) != 2 or position[0] < 0 or position[1] < 0:
            raise ValueError("addMask : tuple specified for mask position is incorrect.")

        icon = img.open(iconPath).convert("RGBA")
        icon = icon.resize(size).rotate(rotationAngle)

        #Add icon to this background image :
        self.backgroundImage.paste(icon, position, icon)


    def drawText(self, text : str, textFont : font.ImageFont, position : tuple, color = "WHITE") -> None:
        """Write specified text on this image, with the given font and color and at the specified
        position
        ### Parameters :
        * text [in] : text to write on this image
        * textFont [in] : font used to write the text on this image
        * position [in] : position where write the text on this image, as a tuple (x, y)
        * color [in, opt] : color of the text to write, default color is white

        ### Return : not applicable"""
        #Arguments checks :

        if len(position) != 2 or position[0] < 0 or position[1] < 0:
            raise ValueError("addMask : tuple specified for mask position is incorrect.")
        if textFont is None :
            raise ValueError("drawText : Font must be defined")

        #Write text on this image :
        self.drawTool.text(position, text, color, font=textFont)


    def saveImage(self, saveLocationPath : str, format : str = "png") -> None :
        """Save this image at the specified location and format
        ### Parameters :
        * saveLocationPath [in] : path where save this image, as a string
        * format [in, opt] : save format for this image, default is png

        ### Return : not applicable"""

        self.backgroundImage.save(saveLocationPath, format)