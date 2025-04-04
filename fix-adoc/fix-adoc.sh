#!/bin/bash

echo "Running fix-headings-simple.py..."
python3 fix-headings-simple.py

echo "Running remove-links-in-headings.py..."
python3 remove-links-in-headings.py 

echo "Running google-image-path-replace-v2.py..."
python3 google-image-path-replace-v2.py

echo "Running plus-fix.py..."
python3 plus-fix.py

echo "Running replace-spaces.py"
python3 replace-spaces.py

echo "Running add-spaces.py"
python3 add-spaces.py

echo "Running replace-non-breaking-space.py"
python3 replace-non-breaking-space.py 

echo "All the scripts done"
