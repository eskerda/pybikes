import re
import sys
import argparse
import logging

from pathlib import Path

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent
TEMPLATE_SYSTEM = TEMPLATE_DIR / "system.py"
TEMPLATE_DATA = TEMPLATE_DIR / "system.json"

TARGET_DIR = Path(__file__).parent.parent.parent

parser = argparse.ArgumentParser(
    prog="Pybikes Scaffold",
    description="Generates pybikes code",
)
parser.add_argument("classname", help="name of the system")
parser.add_argument("-f", "--force", action="store_true", default=False)

args = parser.parse_args()

filename = re.sub(r"\s+", "_", args.classname).lower()
classname = re.sub(r"\w+", lambda m: m.group(0).capitalize(), args.classname)
classname = re.sub(r"\s+", "", classname)
tagname = re.sub(r"\s+", "-", args.classname).lower()

system = TEMPLATE_SYSTEM.read_text()
system = system.replace("SYSTEM_CLASS", classname)

data = TEMPLATE_DATA.read_text()
data = data.replace("SYSTEM_CLASS", classname)
data = data.replace("SYSTEM_FILENAME", filename)
data = data.replace("SYSTEM_TAG", tagname)

target_system_file = TARGET_DIR / "pybikes" / (filename + ".py")
target_data_file = TARGET_DIR / "pybikes" / "data" / (filename + ".json")

for path in [target_system_file, target_data_file]:
    if path.exists():
        if args.force:
            logger.warning("Overwriting %s", path)
        else:
            logger.error("%s exists, use -f to overwrite", path)
            sys.exit(1)

logger.info("Generating system file: %s", target_system_file)
target_system_file.write_text(system)

logger.info("Generating data file: %s", target_data_file)
target_data_file.write_text(data)

print(f"""
================================================
Here is your '{classname}' implementation

System: pybikes/{filename}.py
Data: pybikes/data/{filename}.json

Run tests by:
$ pytest -k {classname}

Visualize result:
$ make map! T_FLAGS+='-k {classname}'

Happy hacking :)
================================================
""")
