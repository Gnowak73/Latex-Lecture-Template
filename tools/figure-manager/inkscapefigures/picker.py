"""
Call a command line fuzzy matcher to select a figure to edit.

Current supported matchers are:

* choose-gui (https://github.com/chipsenkbeil/choose)
"""
import subprocess
import platform
import shutil

SYSTEM_NAME = platform.system()


def get_picker_cmd(picker_args=None, fuzzy=True):
    """
    Create the shell command that will be run to start the picker.
    """
    if SYSTEM_NAME not in ("Darwin", "Linux"):
        raise ValueError("No supported picker for {}".format(SYSTEM_NAME))

    choose_gui = shutil.which("choose-gui")
    choose_bin = shutil.which("choose")
    if choose_gui:
        args = [choose_gui]
    elif choose_bin:
        args = [choose_bin]
    else:
        raise ValueError("picker not found; please install choose-gui")

    if picker_args is not None:
        args += picker_args

    return [str(arg) for arg in args]


def pick(options, picker_args=None, fuzzy=True):
    optionstr = '\n'.join(option.replace('\n', ' ') for option in options)
    cmd = get_picker_cmd(picker_args=picker_args, fuzzy=fuzzy)
    result = subprocess.run(cmd, input=optionstr, stdout=subprocess.PIPE,
                            universal_newlines=True)
    returncode = result.returncode
    stdout = result.stdout.strip()

    selected = stdout.strip()
    try:
        index = [opt.strip() for opt in options].index(selected)
    except ValueError:
        index = -1

    if returncode == 0:
        key = 0
    elif returncode == 1:
        key = -1
    elif returncode > 9:
        key = returncode - 9

    return key, index, selected
