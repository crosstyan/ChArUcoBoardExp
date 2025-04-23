#!/bin/bash

# Set input folder
INPUT_DIR="board"
DPI=100  # Resolution in DPI

# Iterate over all .pdf files in the folder
for pdf in "$INPUT_DIR"/*.pdf; do
    # Strip .pdf to get base name
    base="${pdf%.pdf}"
    # Convert to PNG
    magick convert -density "$DPI" "$pdf" "${base}.png"
    echo "Converted: $pdf → ${base}.png"
done
