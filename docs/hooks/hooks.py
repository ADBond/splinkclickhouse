import re

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page


def on_files(files: Files, config: MkDocsConfig):
    # add in the root-level CHANGELOG to be available to docs
    file = File(
        path="CHANGELOG.md",
        src_dir=".",
        dest_dir=config["site_dir"],
        use_directory_urls=False,
    )
    files.append(file)

    return files


def semver_greater_equal_to(version_number, in_relation_to):
    SEMVER_REGEX = r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    semver_pattern = re.compile(SEMVER_REGEX)
    if not (semver_match := semver_pattern.fullmatch(version_number)):
        raise ValueError(f"Invalid version format: '{version_number}'")
    if not (ref_match := semver_pattern.fullmatch(in_relation_to)):
        raise ValueError(f"Invalid version format: '{in_relation_to}'")
    for group_level in ("major", "minor", "patch"):
        ver_lev = int(semver_match.group(group_level))
        ref_lev = int(ref_match.group(group_level))
        if ver_lev > ref_lev:
            return True
        elif ver_lev < ref_lev:
            return False
        # if equal we move down a level
    # if all equal then true of course
    return True


def replace_headers(header_line: str):
    FIRST_PYPI_VERSION = "0.2.3"
    # ecample header: "## [0.2.3] - 2024-09-16"
    VERSION_HEADER_REGEX = (
        r"## \[(?P<version>\d+\.\d+\.\d+)\] - " r"(?P<release_date>\d{4}-\d{2}-\d{2})"
    )
    # example link: "[0.1.0]: https://github.com/ADBond/splinkclickhouse/releases/tag/v0.1.0"
    LINK_REGEX = r"\[(?P<version>\d+\.\d+\.\d+)\]: (?P<link>https.+)"

    version_pattern = re.compile(VERSION_HEADER_REGEX)
    link_pattern = re.compile(LINK_REGEX)
    if version_match := version_pattern.fullmatch(header_line):
        version = version_match.group("version")
        release_date = version_match.group("release_date")
        version_title = (
            f"[v{version}]"
            if semver_greater_equal_to(version, FIRST_PYPI_VERSION)
            else f"v{version}"
        )
        header_line = (
            f"## {version_title}\n\n"
            f"Released on {release_date}. See "
            f"[v{version} release on GitHub]"
            f"(https://github.com/ADBond/splinkclickhouse/releases/tag/v{version})"
        )
    elif link_match := link_pattern.fullmatch(header_line):
        version = link_match.group("version")
        if version == "Unreleased":
            # unreleased can just link to main
            link = "https://github.com/ADBond/splinkclickhouse/tree/main"
        elif semver_greater_equal_to(version, FIRST_PYPI_VERSION):
            link = f"https://pypi.org/project/splinkclickhouse/{version}/"
        else:
            link = None
        if link:
            header_line = f"[v{version}]: {link}"
        else:
            header_line = ""
    return header_line


def on_page_markdown(markdown: str, page: Page, config: MkDocsConfig, files: Files):
    if page.title != "Version history":
        return

    markdown_lines = markdown.split("\n")
    # replace preamble - hardcode lines to replace
    INITIAL_LINES_TO_DELETE = 7
    markdown_lines = ["# Version history", ""] + markdown_lines[
        (INITIAL_LINES_TO_DELETE):
    ]
    # replace github links with pypi in titles, where possible
    # strip out dates into body
    # also add github release links
    new_markdown = "\n".join(map(replace_headers, markdown_lines))
    return new_markdown
