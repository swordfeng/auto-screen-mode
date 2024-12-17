import ctypes
import enum

# Windows display configuration constants
class DisplayConfigFlags(enum.IntFlag):
    SDC_TOPOLOGY_INTERNAL = 0x00000001
    SDC_TOPOLOGY_CLONE = 0x00000002
    SDC_TOPOLOGY_EXTEND = 0x00000004
    SDC_TOPOLOGY_EXTERNAL = 0x00000008
    SDC_USE_SUPPLIED_DISPLAY_CONFIG = 0x00000020
    SDC_VALIDATE = 0x00000040
    SDC_APPLY = 0x00000080
    SDC_NO_OPTIMIZATION = 0x00000100
    SDC_SAVE_TO_DATABASE = 0x00000200
    SDC_ALLOW_CHANGES = 0x00000400
    SDC_PATH_PERSIST_IF_REQUIRED = 0x00000800
    SDC_FORCE_MODE_ENUMERATION = 0x00001000
    SDC_VIRTUAL_MODE_AWARE = 0x00010000

class DisplayConfigManager:
    def __init__(self):
        # Load user32.dll
        self.user32 = ctypes.windll.user32
        
        self.user32.SetDisplayConfig.argtypes = [
            ctypes.c_uint,   # numPathArrayElements
            ctypes.c_void_p, # pathArray
            ctypes.c_uint,   # numModeInfoArrayElements
            ctypes.c_void_p, # modeInfoArray
            ctypes.c_uint    # flags
        ]
        self.user32.SetDisplayConfig.restype = ctypes.c_long

    def set_display_config(self, flags=DisplayConfigFlags.SDC_APPLY):
        # Call SetDisplayConfig with the current topology
        result = self.user32.SetDisplayConfig(0, 0, 0, 0, flags)

        # Check the return value
        if result == 0:
            print("Display configuration applied successfully.")
        else:
            print(f"Failed to set display config. Return code: {result}")
            raise ctypes.WinError(result)