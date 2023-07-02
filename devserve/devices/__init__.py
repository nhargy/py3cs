__all__ = ["I will get rewritten"]
# Don't modify the line above, or this line!
import automodinit
automodinit.automodinit(__name__, __file__, globals())
del automodinit
# Anything else you want can go after here, it won't get modified.
from .device import Device
device_directory = {cls.__name__: cls for cls in Device.__subclasses__()}
