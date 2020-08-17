import gi
import glob
import os.path
import re
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class DLLExplorer(Gtk.Window):
    objdump = '/usr/bin/x86_64-w64-mingw32-objdump'
    dir_target = '/home/bitwalk/test/usr/local/bin'
    dir_mingw64 = '/usr/x86_64-w64-mingw32/sys-root/mingw/bin'
    p = re.compile(r'\s*DLL\sName:\s(.*\.dll)')
    list_dll = list()
    list_rpm = list()

    def __init__(self):
        Gtk.Window.__init__(self, title='DLL Explorer')
        self.set_default_size(0, 0)

        but = Gtk.Button(label='START')
        but.connect('clicked', self.on_start, self.dir_target)
        self.add(but)

    def on_start(self, button, dir):
        print('START')

        list_file_bin = glob.glob(os.path.join(dir, '*'))
        for file_bin in list_file_bin:
            print(file_bin)
            self.check_dll(file_bin)

        self.list_dll = list(set(self.list_dll))
        for dll in self.list_dll:
            self.check_rpm(dll)

        self.list_rpm = list(set(self.list_rpm))
        self.list_rpm.sort()
        for rpm in self.list_rpm:
            print(rpm)

        print(len(self.list_rpm))

    def check_dll(self, filename):
        res = subprocess.run([self.objdump, '-p', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in res.stdout.decode("utf8").strip().split('\n'):
            m = self.p.match(line)
            if m:
                file_dll = m.group(1)
                file_dll_full = os.path.join(self.dir_mingw64, file_dll)
                # check if file_dll_full exists
                if os.path.exists(file_dll_full):
                    self.list_dll.append(file_dll)
                    # check DLL recursively
                    self.check_dll(file_dll_full)

    def check_rpm(self, dll):
        dll_full = os.path.join(self.dir_mingw64, dll)
        res = subprocess.run(['rpm', '-qf', dll_full], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.list_rpm.append(res.stdout.decode("utf8").strip())


# -----------------------------------------------------------------------------
#  MAIN
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    win = DLLExplorer()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
# ---
# PROGRAM END
