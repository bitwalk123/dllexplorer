import gi
import glob
import os
import os.path
import re
import shutil
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


# =============================================================================
#  file_copy
#
#  arguments:
#    src - source file in full path
#    dst - destinate file in full path
# =============================================================================
def file_copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


# -----------------------------------------------------------------------------
#  DirTree
#  directory tree
# -----------------------------------------------------------------------------
class DirTree():
    root1 = None
    root2 = None
    tree1 = None
    tree2 = None
    store1 = None
    store2 = None
    dir_root = None
    app_root = None
    pkg_root = None
    list_src = list()

    def __init__(self, tree1, tree2, store1, store2):
        self.tree1 = tree1
        self.tree2 = tree2
        self.store1 = store1
        self.store2 = store2

    # -------------------------------------------------------------------------
    #  copy
    # -------------------------------------------------------------------------
    def copy(self):
        regex1 = self.app_root + '/(.*)'
        pattern1 = re.compile(regex1)
        for file in self.list_src:
            # BUILT files
            match1 = pattern1.match(file)
            if match1:
                file_dst = match1.group(1)
                file_dst = os.path.join(self.pkg_root, file_dst)
                print(file_dst)
                file_copy(file, file_dst)
            else:
                print('Error!')

        # Runtime check
        runtime = RunTime(os.path.join(self.app_root, 'bin'))
        runtime.start()

        regex2 = runtime.get_mingw64_topdir() + '/(.*)'
        pattern2 = re.compile(regex2)

        regex3 = '/usr/(.*)'
        pattern3 = re.compile(regex3)

        regex4 = '/usr/share/(.*)'
        pattern4 = re.compile(regex4)

        for file in runtime.list_file:
            match2 = pattern2.match(file)
            if match2:
                file_dst = match2.group(1)
                file_dst = os.path.join(self.pkg_root, file_dst)
                print(file_dst)
                file_copy(file, file_dst)
            else:
                match3 = pattern3.match(file)
                if match3:
                    # only copy /usr/share/*.
                    # others are igonored without error
                    match4 = pattern4.match(file)
                    if match4:
                        file_dst = match4.group(1)
                        file_dst = os.path.join(self.pkg_root, "share", file_dst)
                        print(file_dst)
                        file_copy(file, file_dst)
                else:
                    print('Error!')

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #  display file tree at destination pane (left)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.add_tree_iter(self.tree2, self.store2, self.root2, self.pkg_root)

    # -------------------------------------------------------------------------
    #  show_app
    # -------------------------------------------------------------------------
    def show_app(self, dir):
        # INITIALIZE
        self.dir_root = dir
        self.app_root = None
        self.list_src = list()
        iter = self.store1.get_iter_first()
        if iter is not None:
            self.store1.clear()

        self.root1 = self.store1.append(None, [self.dir_root])

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #  display file tree at source pane (right)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.add_tree_iter(self.tree1, self.store1, self.root1, self.dir_root)

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

            # print(file)
        # print(self.app_root)

    # -------------------------------------------------------------------------
    #  show_app
    # -------------------------------------------------------------------------
    def show_pkg(self, dir):
        self.pkg_root = dir

        self.root2 = self.store2.append(None, [self.pkg_root])

    # -------------------------------------------------------------------------
    #  add_tree_iter
    # -------------------------------------------------------------------------
    def add_tree_iter(self, tree, store, iter_parent, dir_parent):
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
            iter = store.append(iter_parent, [os.path.basename(dir)])
            self.add_tree_iter(tree, store, iter, dir)

        list_file.sort()
        for file in list_file:
            iter = store.append(iter_parent, [os.path.basename(file)])
            self.tree_expand(tree, store, iter)
            self.list_src.append(file)

    # -------------------------------------------------------------------------
    #  compare_dir
    # -------------------------------------------------------------------------
    def compare_dir(self, dirA, dirB):
        if dirA != dirB:
            if len(dirA) > 1:
                self.compare_updir(dirA, dirB)
            else:
                print('Error!')

    # -------------------------------------------------------------------------
    #  compare_updir
    # -------------------------------------------------------------------------
    def compare_updir(self, dirA, dirB):
        dirC = os.path.dirname(dirA)
        dirD = os.path.dirname(dirB)
        if dirC == dirD:
            self.app_root = dirC
        else:
            if len(dirC.split('/')) > 1:
                self.compare_updir(dirC, dirD)

    # -------------------------------------------------------------------------
    #  tree_expand
    # -------------------------------------------------------------------------
    def tree_expand(self, tree, store, iter):
        path = store.get_path(iter)
        tree.expand_to_path(path)


# -----------------------------------------------------------------------------
#  RunTime
#  run time dll search
# -----------------------------------------------------------------------------
class RunTime():
    dir_target = None
    objdump = '/usr/bin/x86_64-w64-mingw32-objdump'
    dir_mingw64 = '/usr/x86_64-w64-mingw32/sys-root/mingw'
    bin_mingw64 = os.path.join(dir_mingw64, 'bin')
    include_mingw64 = os.path.join(dir_mingw64, 'include')
    pattern1 = re.compile(r'\s*DLL\sName:\s(.*\.dll)')
    pattern2 = re.compile(bin_mingw64)
    pattern3 = re.compile(include_mingw64)
    pattern4 = re.compile(r'^/usr/share/man/')
    list_dll = list()
    list_dll_NA = list()
    list_rpm = list()
    list_file = list()
    # default theme of GNOME used in window decoration
    rpm_theme = 'adwaita-icon-theme'

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
            self.get_DLLs(file_bin, self.list_dll, self.list_dll_NA, self.bin_mingw64)

        # set unique DLLs
        self.list_dll = list(set(self.list_dll))
        self.list_dll_NA = list(set(self.list_dll_NA))
        self.list_dll_NA.sort()
        # get RPM package contains specified DLL
        for dll in self.list_dll:
            dll_full = os.path.join(self.bin_mingw64, dll)
            self.list_file.append(dll_full)
            self.get_RPM(dll_full, self.list_rpm)

        # add icon theme used for window decoration
        self.list_rpm.append(self.rpm_theme)
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

        # for dll in self.list_dll_NA:
        #    print(dll)

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
            match = self.pattern1.match(line)
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
            if os.path.isfile(file):

                # /usr/x86_64-w64-mingw32/sys-root/mingw/bin
                match2 = self.pattern2.match(file)
                if match2:
                    continue

                # /usr/x86_64-w64-mingw32/sys-root/mingw/include
                match3 = self.pattern3.match(file)
                if match3:
                    continue

                # /usr/share/man/
                match4 = self.pattern4.match(file)
                if match4:
                    continue

                filelist.append(file)

    # -------------------------------------------------------------------------
    #  get_mingw64_topdir - get top directory of MinGW64 system
    #
    #  argument
    #    (none)
    #
    #  return
    #    (none)
    # -------------------------------------------------------------------------
    def get_mingw64_topdir(self):
        # retern after aliminating 'bin'
        return (self.dir_mingw64)


# -----------------------------------------------------------------------------
#  img
#  Image Facility
# -----------------------------------------------------------------------------
class img(Gtk.Image):
    IMG_FOLDER = "img/folder-128.png"
    IMG_PLAY = "img/play-128.png"

    def __init__(self):
        Gtk.Image.__init__(self)

    # -------------------------------------------------------------------------
    #  get_image
    # -------------------------------------------------------------------------
    def get_image(self, image_name, size=24):
        pixbuf = self.get_pixbuf(image_name, size)
        return Gtk.Image.new_from_pixbuf(pixbuf)

    # -------------------------------------------------------------------------
    #  get_pixbuf
    # -------------------------------------------------------------------------
    def get_pixbuf(self, image_name, size=24):
        name_file = self.get_file(image_name)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(name_file)
        pixbuf = pixbuf.scale_simple(size, size, GdkPixbuf.InterpType.BILINEAR)
        return pixbuf

    # -------------------------------------------------------------------------
    #  get_file
    # -------------------------------------------------------------------------
    def get_file(self, image_name):
        if image_name == "folder":
            name_file = self.IMG_FOLDER
        elif image_name == "play":
            name_file = self.IMG_PLAY
        return name_file

# ---
# END OF PROGRAM
