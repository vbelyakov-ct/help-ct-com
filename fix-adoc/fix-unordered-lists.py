import os
import re
import argparse
from pathlib import Path


def process_file(file_path):
    """Process a single file according to the formatting rules."""
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Define the pattern to search for:
        # Look for "* " that is preceded by non-whitespace characters on the same line
        pattern = r'(^|\n)([^\s\n].*?)(\* )'

        # Function to process each match
        def replace_match(match):
            prefix = match.group(1)  # Newline or start of string
            text_before = match.group(2)  # Text before "* "
            marker = match.group(3)  # The "* " pattern
            
            # Return the prefix, the text before, a newline, and the marker
            return f"{prefix}{text_before}\n{marker}"

        # Apply the replacement
        modified_content = re.sub(pattern, replace_match, content)

        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)

        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def process_directory(directory_path, file_extensions=None):
    """Process all files in the specified directory."""
    directory = Path(directory_path)
    if not directory.is_dir():
        print(f"Error: {directory_path} is not a valid directory.")
        return
    
    # Get all files in the directory
    files = [f for f in directory.glob('**/*') if f.is_file()]
    
    # Filter by extensions if specified
    if file_extensions:
        extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in file_extensions]
        files = [f for f in files if f.suffix.lower() in extensions]
    
    total_files = len(files)
    processed = 0
    
    for file_path in files:
        if process_file(file_path):
            processed += 1
            print(f"Processed: {file_path}")
    
    print(f"Completed: {processed}/{total_files} files processed successfully.")


def get_user_input():
    """Get directory and extensions from user input."""
    directory = input("Enter the directory path to process: ").strip()
    
    # Validate directory
    while not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a valid directory.")
        directory = input("Please enter a valid directory path: ").strip()
    
    extensions_input = input("Enter file extensions to process (space separated, press Enter for all files): ").strip()
    
    if extensions_input:
        extensions = extensions_input.split()
    else:
        extensions = None
    
    return directory, extensions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Format text files by moving content after "* " to a new line.')
    parser.add_argument('--directory', help='Directory containing files to process')
    parser.add_argument('--extensions', nargs='+', help='File extensions to process (e.g., txt md adoc)')
    
    args = parser.parse_args()
    
    # If directory wasn't provided via command line, ask for it
    if args.directory:
        directory = args.directory
        extensions = args.extensions
    else:
        directory, extensions = get_user_input()
    
    process_directory(directory, extensions)