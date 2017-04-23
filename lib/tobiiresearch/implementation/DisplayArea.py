class DisplayArea(object):
    '''Represents the corners in space of the active display area, and its size.

    Return value from EyeTracker.get_display_area.
    '''

    def __init__(self, display_area):
        if ((not isinstance(display_area, dict) or
             not isinstance(display_area["bottom_left"], tuple) or
             not isinstance(display_area["bottom_right"], tuple) or
             not isinstance(display_area["height"], float) or
             not isinstance(display_area["top_left"], tuple) or
             not isinstance(display_area["top_right"], tuple) or
             not isinstance(display_area["width"], float))):
            raise ValueError(
                "You shouldn't create DisplayArea objects yourself.")

        self.__bottom_left = display_area["bottom_left"]
        self.__bottom_right = display_area["bottom_right"]
        self.__height = display_area["height"]
        self.__top_left = display_area["top_left"]
        self.__top_right = display_area["top_right"]
        self.__width = display_area["width"]

    @property
    def bottom_left(self):
        '''Gets the bottom left corner of the active display area as a three valued tuple.
        '''
        return self.__bottom_left

    @property
    def bottom_right(self):
        '''Gets the bottom left corner of the active display area as a three valued tuple.
        '''
        return self.__bottom_right

    @property
    def height(self):
        '''Gets the height in millimeters of the active display area.
        '''
        return self.__height

    @property
    def top_left(self):
        '''Gets the top left corner of the active display area as a three valued tuple.
        '''
        return self.__top_left

    @property
    def top_right(self):
        '''Gets the top right corner of the active display area as a three valued tuple.
        '''
        return self.__top_right

    @property
    def width(self):
        '''Gets the width in millimeters of the active display area.
        '''
        return self.__width
