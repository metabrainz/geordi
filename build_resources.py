#!/usr/bin/env python
import os
import sys
import subprocess
import shutil

ROOT_DIR        = os.path.abspath(os.path.dirname(__file__))
NODE_MODULES    = os.path.join(ROOT_DIR, "node_modules")
STATIC_DIR      = os.path.join(ROOT_DIR, "geordi/geordi/static");
BUILD_DIR       = STATIC_DIR + "/build";
STYLES_DIR      = STATIC_DIR + "/styles";


def subprocess_call(*args, **kwargs):
    print " ".join(args[0])
    subprocess.call(*args, **kwargs)


def scripts():
    scripts_build_dir = os.path.join(BUILD_DIR, "scripts")

    if os.path.isdir(scripts_build_dir):
        shutil.rmtree(scripts_build_dir)

    subprocess_call(["node", os.path.join(NODE_MODULES, "requirejs/bin/r.js"), "-o", "build.js"])


def styles():
    styles_build_dir = os.path.join(BUILD_DIR, "styles")

    if os.path.isdir(styles_build_dir):
        shutil.rmtree(styles_build_dir)

    os.makedirs(styles_build_dir)

    lessc = os.path.join(NODE_MODULES, "less/bin/lessc")

    for fname in os.listdir(STYLES_DIR):
        (name, ext) = os.path.splitext(fname)
        if ext == ".less":
            with open(os.path.join(styles_build_dir, name + ".css"), "w") as fp:
                subprocess_call([lessc, os.path.join(STYLES_DIR, fname)], stdout=fp)


if __name__ == "__main__":
    actions = {
        "scripts": scripts,
        "styles": styles
    }
    [actions[name]() for name in (sys.argv[1:] or ("scripts", "styles"))]
