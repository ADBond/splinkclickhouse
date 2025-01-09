import os

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files


def on_files(files: Files, config: MkDocsConfig):

    file = File(
        path="CHANGELOG.md",
        src_dir=".",
        dest_dir=config["site_dir"],
        use_directory_urls=False,
    )
    files.append(file)

    return files
