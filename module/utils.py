import gi
import glob
import os.path
import re
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


# -----------------------------------------------------------------------------
#  DirTree
#  directory tree
# -----------------------------------------------------------------------------
class DirTree():
    tree = None
    store = None
    dir_root = None
    app_root = None
    list_src = list()

    def __init__(self, tree, store, dir):
        self.tree = tree
        self.store = store
        self.dir_root = dir

    def show(self):
        root = self.store.append(None, [self.dir_root])
        top = self.dir_root
        self.add_tree_node(root, top)

        for file in self.list_src:
            if self.app_root is None:
                self.app_root = os.path.dirname(file)
            else:
                dir1 = self.app_root
                dir2 = os.path.dirname(file)

                while len(dir1.split('/')) > len(dir2.split('/')):
                    dir1 = os.path.dirname(dir1)
                while len(dir1.split('/')) < len(dir2.split('/')):
                    dir2 = os.path.dirname(dir2)

                self.compare_dir(dir1, dir2)

            print(file)
        print(self.app_root)

    def add_tree_node(self, node_parent, dir_parent):
        list_obj = glob.glob(os.path.join(dir_parent, '*'))

        list_dir = list()
        list_file = list()
        for obj in list_obj:
            if os.path.isdir(obj):
                list_dir.append(obj)
            if os.path.isfile(obj):
                list_file.append(obj)

        list_dir.sort()
        for dir in list_dir:
            node = self.store.append(node_parent, [os.path.basename(dir)])
            self.add_tree_node(node, dir)

        list_file.sort()
        for file in list_file:
            node = self.store.append(node_parent, [os.path.basename(file)])
            self.tree_node_expand(node)
            self.list_src.append(file)

    def compare_dir(self, dirA, dirB):
        if dirA != dirB:
            if len(dirA) > 1:
                self.compare_updir(dirA, dirB)
            else:
                print('Error!')

    def compare_updir(self, dirA, dirB):
        dirC = os.path.dirname(dirA)
        dirD = os.path.dirname(dirB)
        if dirC == dirD:
            self.app_root = dirC
        else:
            if len(dirC.split('/')) > 1:
                self.compare_updir(dirC, dirD)

    def tree_node_expand(self, node):
        path = self.store.get_path(node)
        self.tree.expand_to_path(path)


# -----------------------------------------------------------------------------
#  img
#  Image Facility
# -----------------------------------------------------------------------------
class img(Gtk.Image):
    IMG_FOLDER = "img/folder-128.png"
    IMG_PLAY = "img/play-128.png"

    def __init__(self):
        Gtk.Image.__init__(self)

    def get_image(self, image_name, size=24):
        pixbuf = self.get_pixbuf(image_name, size)
        return Gtk.Image.new_from_pixbuf(pixbuf)

    def get_pixbuf(self, image_name, size=24):
        name_file = self.get_file(image_name)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(name_file)
        pixbuf = pixbuf.scale_simple(size, size, GdkPixbuf.InterpType.BILINEAR)
        return pixbuf

    def get_file(self, image_name):
        if image_name == "folder":
            name_file = self.IMG_FOLDER
        elif image_name == "play":
            name_file = self.IMG_PLAY
        return name_file


# -----------------------------------------------------------------------------
#  RunTime
#  run time dll search
# -----------------------------------------------------------------------------
class RunTime():
    dir_target = None
    objdump = '/usr/bin/x86_64-w64-mingw32-objdump'
    dir_mingw64 = '/usr/x86_64-w64-mingw32/sys-root/mingw/bin'
    pattern = re.compile(r'\s*DLL\sName:\s(.*\.dll)')
    list_dll = list()
    list_dll_NA = list()
    list_rpm = list()
    list_file = list()

    # CONSTRUCTOR
    def __init__(self, dir):
        self.dir_target = dir

    # -------------------------------------------------------------------------
    #  start - start checking runtime DLL and related files
    # -------------------------------------------------------------------------
    def start(self):
        # set full path to search target binnary files
        list_file_bin = glob.glob(os.path.join(self.dir_target, '*'))
        # get relevant runtime DLLs
        for file_bin in list_file_bin:
            print(file_bin)
            self.get_DLLs(file_bin, self.list_dll, self.list_dll_NA, self.dir_mingw64)

        # set unique DLLs
        self.list_dll = list(set(self.list_dll))
        self.list_dll_NA = list(set(self.list_dll_NA))
        self.list_dll_NA.sort()
        # get RPM package contains specified DLL
        for dll in self.list_dll:
            dll_full = os.path.join(self.dir_mingw64, dll)
            self.get_RPM(dll_full, self.list_rpm)

        # set unique RPMs
        self.list_rpm = list(set(self.list_rpm))
        # sort list of RPMs
        self.list_rpm.sort()
        # get list of files in specified RPM
        for rpm in self.list_rpm:
            self.get_file_in_rpm(rpm, self.list_file)

        # sort list of files in RPMs
        self.list_file.sort()

        # _/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_
        #  FOLLOWINGS ARE TESTING PURPOSE!

        for file in self.list_file:
            print(file)

        print(len(self.list_file))

        for dll in self.list_dll_NA:
            print(dll)

    # -------------------------------------------------------------------------
    #  get_DLLs - get related DLLs recursively
    #
    #  argument
    #    filename   : file in full path to be checked DLLs.
    #    dlllist    : list of DLL which is found and exists
    #    dlllist_na : list of DLL which is found and NOT exist
    #    dir        : path of DLL
    #
    #  return
    #    (none)
    # -------------------------------------------------------------------------
    def get_DLLs(self, filename, dlllist, dlllist_na, dir):
        res = subprocess.run(
            [self.objdump, '-p', filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        for line in res.stdout.decode("utf8").strip().split('\n'):
            match = self.pattern.match(line)
            if match:
                dll = match.group(1)
                dll_full = os.path.join(dir, dll)
                # check if file_dll_full exists
                if os.path.exists(dll_full):
                    # list of existent DLLs
                    dlllist.append(dll)
                    # check DLL recursively
                    self.get_DLLs(dll_full, dlllist, dlllist_na, dir)
                else:
                    # list of non-existent DLLs
                    dlllist_na.append(dll)

    # -------------------------------------------------------------------------
    #  get_DLLs - get RPM name which specified DLL belongs to
    #
    #  argument
    #    dll     : actual DLL name in full path
    #    rpmlist : rpm list to store
    #
    #  return
    #    (none)
    # -------------------------------------------------------------------------
    def get_RPM(self, dll, rpmlist):
        res = subprocess.run(
            ['rpm', '-qf', dll],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        rpm = res.stdout.decode("utf8").strip()
        rpmlist.append(rpm)

    # -------------------------------------------------------------------------
    #  get_file_in rpm - list of files in specified RPM
    #
    #  argument
    #    rpm      : RPM name
    #    filelist : file list to store
    #
    #  return
    #    (none)
    # -------------------------------------------------------------------------
    def get_file_in_rpm(self, rpm, filelist):
        res = subprocess.run(
            ['rpm', '-ql', rpm],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        for file in res.stdout.decode("utf8").strip().split('\n'):
            filelist.append(file)

# ---
# END OF PROGRAM
