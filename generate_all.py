#!/usr/bin/env python3
""" Generate all slide decks from the .md files in the 'catalogs/' directory and below. """
import os
import sys
import fnmatch
from tqdm.autonotebook import tqdm
from generate import generate


print(f"Usage: {sys.argv[0]} [pdf|pptx|html] [--zip]")
FILE_EXT = ".pdf"
if len(sys.argv) >= 2:
    FILE_EXT = f".{sys.argv[1]}"
if len(sys.argv) >= 3:
    OPTIONS = sys.argv[2:]
else:
    OPTIONS = None

# Get the list of all .md files in the 'catalogs/' directory and its subdirectories
md_files = []
for root, dirs, files in os.walk('catalogs/'):
    for file in fnmatch.filter(files, '*.md'):
        #print(f"Found file {os.path.join(root, file)}")
        md_files.append(os.path.join(root, file))


# Iterate over all .md files with a progress bar
for md_file in tqdm(md_files, unit="file", desc='Processing files'):
    #print(f'Processing {md_file}')

    # Replace all "/" in the filename with "-"
    output_file = md_file.replace('catalogs/', 'output/').replace('.md', FILE_EXT)
    #print(f'Generate     {output_file} ...')

    # Generate the output file
    generate(md_file, output_file, OPTIONS)
