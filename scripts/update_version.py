# script to update package version in relevant files
# this is not fancy, so you should probably check results
# run from repo root.

import argparse
import re
from datetime import datetime
from pathlib import Path

parser = argparse.ArgumentParser(
    prog="VersionUpdater",
    description="Update files for new package version"
)
parser.add_argument("new_version", help="New version number in X.X.X format")
args = parser.parse_args()
new_version = args.new_version

version_format = r"[0-9]+\.[0-9]+\.[0-9]+"
if not re.search(version_format, new_version):
    raise ValueError(f"Bad version supplied: {new_version}. Should be 'X.X.X' format")

package_file = Path("splinkclickhouse") / "__init__.py"
pyproject_file = Path(".") / "pyproject.toml"
readme_file = Path(".") / "README.md"
changelog_file = Path(".") / "CHANGELOG.md"

with open(package_file, "r") as f:
    init_text = f.read()

with open(pyproject_file, "r") as f:
    pyproject_text = f.read()

with open(readme_file, "r") as f:
    readme_text = f.read()

init_version_template = '__version__ = "{version_literal}"'
pyproject_version_template = 'version = "{version_literal}"'
readme_version_template = "splinkclickhouse.git@v{version_literal}"

version_regex_group = f"({version_format})"

init_version_regex = init_version_template.format(version_literal=version_regex_group)

m = re.search(init_version_regex, init_text)
prev_version = m.group(1)

if new_version == prev_version:
    raise ValueError(
        f"You haven't incremented version! Received current version {prev_version}"
    )

updated_init_text = re.sub(
    init_version_regex,
    init_version_template.format(version_literal=new_version),
    init_text,
)
updated_pyproject_text = re.sub(
    pyproject_version_template.format(version_literal=version_regex_group),
    pyproject_version_template.format(version_literal=new_version),
    pyproject_text,
)
updated_readme_text = re.sub(
    readme_version_template.format(version_literal=version_regex_group),
    readme_version_template.format(version_literal=new_version),
    readme_text,
)

with open(package_file, "w+") as f:
    f.write(updated_init_text)

with open(pyproject_file, "w+") as f:
    f.write(updated_pyproject_text)

with open(readme_file, "w+") as f:
    f.write(updated_readme_text)

# update changelog - takes a different format from the others
release_date = datetime.today().strftime("%Y-%m-%d")

with open(changelog_file, "r") as f:
    changelog_text = f.read()

updated_changelog_text = changelog_text.replace(
    "## Unreleased",
    (
        "## Unreleased\n"
        "\n"
        f"## [{new_version}] - {release_date}"
    )
)
unreleased_link_template = "[unreleased]: https://github.com/ADBond/splinkclickhouse/compare/v{version_literal}...HEAD"
new_link = f"[{new_version}]: https://github.com/ADBond/splinkclickhouse/compare/v{prev_version}...v{new_version}"

updated_changelog_text = updated_changelog_text.replace(
    unreleased_link_template.format(version_literal=prev_version),
    unreleased_link_template.format(version_literal=new_version) + "\n" + new_link,
)

with open(changelog_file, "w+") as f:
    f.write(updated_changelog_text)
