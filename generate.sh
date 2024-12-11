#!/bin/bash

# Check if two arguments were provided
if [ "$#" -ne 2 ]; then
  echo "Markdown to HTML/PDF converter"
  echo "Usage: $0 <input_file> <output_file>"
  echo "Sample: $0 input.md output.pdf"
  echo "Attention: run setup.sh before using this script to install NodeJS and MARP"
  exit 1
fi

# Assign arguments to variables for clarity
input_file="$1"
output_file="$2"
root_dir=$(dirname "$0")

# Generate the output file
npx marp --html --pdf-outlines --pdf-outlines.pages=false --allow-local-files --theme "$root_dir/theme/fhtw.css" "$input_file" -o "$output_file"
