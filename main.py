import time
import traceback
import win32api
import win32gui
import win32con
import win32gui_struct
import re
from display import DisplayConfigFlags, DisplayConfigManager

# Ioevent.h
GUID_DEVINTERFACE_USB_DEVICE = "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"
# IKBC C104 Keyboard
DEV_MONITOR = ("04B4", "4042")

display_manager = DisplayConfigManager()

class USBMonitor:
    def __init__(self):
        win32gui.InitCommonControls()
        self.hinst = win32api.GetModuleHandle(None)
        # Create a window to receive system messages
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = 'USBDeviceMonitor'
        win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow(
            wc.lpszClassName, 
            'USB Device Monitor',
            0,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            0,
            0,
            0,
            0,
            self.hinst,
            None
        )
        filter = win32gui_struct.PackDEV_BROADCAST_DEVICEINTERFACE(
            GUID_DEVINTERFACE_USB_DEVICE
        )
        self.dev_notify = win32gui.RegisterDeviceNotification(
            self.hwnd,
            filter,
            win32con.DEVICE_NOTIFY_WINDOW_HANDLE
        )
    
    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_DEVICECHANGE:
            try:
                if wparam == win32con.DBT_DEVICEARRIVAL:
                    vendor, product = parse_usb_name(lparam)
                    print(f"USB Device {vendor}:{product} Connected!")
                    if (vendor, product) == DEV_MONITOR:
                        # Connected, set to extend mode
                        display_manager.set_display_config(
                            DisplayConfigFlags.SDC_TOPOLOGY_EXTEND | 
                            DisplayConfigFlags.SDC_APPLY
                        )
                elif wparam == win32con.DBT_DEVICEREMOVECOMPLETE:
                    vendor, product = parse_usb_name(lparam)
                    print(f"USB Device {vendor}:{product} Disconnected!")
                    if (vendor, product) == DEV_MONITOR:
                        # Disconnected, set to primary mode
                        display_manager.set_display_config(
                            DisplayConfigFlags.SDC_TOPOLOGY_INTERNAL | 
                            DisplayConfigFlags.SDC_APPLY
                        )
            except:
                traceback.print_exc()
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def start_monitoring(self):
        print("USB Device Monitoring Started...")
        try:
            # Start the message pump
            while True:
                win32gui.PumpWaitingMessages()
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("USB Monitoring Stopped.")

USB_MATCHER = re.compile(r"USB#VID_([0-9A-F]{4})&PID_([0-9A-F]{4})")
def parse_usb_name(lparam):
    try:
        info = win32gui_struct.UnpackDEV_BROADCAST(lparam)
        match = USB_MATCHER.search(info.name)
        if match:
            return match.group(1), match.group(2)
    except Exception as e:
        print(e)

def main():
    # Create and start the USB monitor
    usb_monitor = USBMonitor()
    usb_monitor.start_monitoring()

if __name__ == "__main__":
    main()