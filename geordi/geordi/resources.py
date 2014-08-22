import os
import shutil
from subprocess import call, Popen, PIPE
from flask import current_app
from flask.ext.script import Manager

NODE_MODULES = Popen(["npm", "bin"], stdout=PIPE).communicate()[0].strip()

resources_manager = Manager(usage="Compile various static resources.")

@resources_manager.command
def scripts():
    """Combine and minify JavaScript using the r.js optimizer."""
    scripts_build_dir = os.path.join(current_app.root_path, "static/build/scripts")

    if os.path.isdir(scripts_build_dir):
        shutil.rmtree(scripts_build_dir)

    subprocess_call(["node", os.path.join(NODE_MODULES, "r.js"), "-o", os.path.join(current_app.root_path, "../../build.js")])

@resources_manager.command
def styles():
    """Compile .less files into .css."""
    styles_dir = os.path.join(current_app.root_path, "static/styles")
    styles_build_dir = os.path.join(current_app.root_path, "static/build/styles")

    if os.path.isdir(styles_build_dir):
        shutil.rmtree(styles_build_dir)

    os.makedirs(styles_build_dir)

    lessc = os.path.join(NODE_MODULES, "lessc")

    for fname in os.listdir(styles_dir):
        (name, ext) = os.path.splitext(fname)
        if ext == ".less":
            with open(os.path.join(styles_build_dir, name + ".css"), "w") as fp:
                subprocess_call([lessc, os.path.join(styles_dir, fname)], stdout=fp)

@resources_manager.command
def lodash():
    """Create a custom lodash build."""
    subprocess_call([
        os.path.join(NODE_MODULES, "lodash"),
        "modern",
        "exports=amd",
        "include=any,all,each,filter,reject,invoke,map,assign,clone",
        "-d",
        "-o",
        os.path.relpath(os.path.join(current_app.root_path, "static/scripts/lib/lodash.js"))
    ])

@resources_manager.command
def all():
    """Compile both styles and scripts. Does not include building lodash."""
    styles()
    scripts()

def subprocess_call(*args, **kwargs):
    print " ".join(args[0])
    call(*args, **kwargs)
