import os

def generate_nav_adoc(root_dir):
    """
    Generates a nav.adoc file containing a hierarchical unordered list of xref links
    to .adoc files, reflecting the folder structure through indentation.
    Folder names themselves are not included as list items.
    Links will have empty brackets [] and no extra spaces between '*' and 'xref:'.
    If a folder contains 'index.adoc', it's listed at a higher level, and other .adoc files
    in the same folder are nested under it.

    Args:
        root_dir (str): The path to the root directory.
    """
    if not os.path.isdir(root_dir):
        print(f"Error: The specified path '{root_dir}' is not a valid directory.")
        return

    nav_content = []
    nav_content.append("// This file was generated automatically by a Python script.")
    nav_content.append("// Do not edit manually unless you know what you're doing.")
    nav_content.append("")

    def process_directory_recursive(current_dir, level):
        # Get all entries (files and directories) in the current directory
        # Sort them for consistent output
        entries = sorted(os.listdir(current_dir), key=lambda e: (not os.path.isdir(os.path.join(current_dir, e)), e.lower()))

        dirs = [e for e in entries if os.path.isdir(os.path.join(current_dir, e))]
        all_adoc_files = [e for e in entries if os.path.isfile(os.path.join(current_dir, e)) and e.lower().endswith(".adoc")]

        index_adoc_present = False
        other_adoc_files = []

        if "index.adoc" in all_adoc_files:
            index_adoc_present = True
            all_adoc_files.remove("index.adoc") # Remove it to process separately
            other_adoc_files = all_adoc_files # Remaining files are "other"

            # Add index.adoc at the current hierarchy level
            index_full_path = os.path.join(current_dir, "index.adoc")
            index_relative_path = os.path.relpath(index_full_path, root_dir)
            nav_content.append(f"{'*' * (level + 1)} xref:{index_relative_path}[]")

            # Now, process other .adoc files in this directory nested under index.adoc
            for filename in other_adoc_files:
                file_full_path = os.path.join(current_dir, filename)
                file_relative_path = os.path.relpath(file_full_path, root_dir)
                # These files are one level deeper than index.adoc
                nav_content.append(f"{'*' * (level + 2)} xref:{file_relative_path}[]")
        else:
            # No index.adoc, so all .adoc files are treated as normal children of the folder
            for filename in all_adoc_files:
                file_full_path = os.path.join(current_dir, filename)
                file_relative_path = os.path.relpath(file_full_path, root_dir)
                nav_content.append(f"{'*' * (level + 1)} xref:{file_relative_path}[]")

        # Recursively process subdirectories
        for dirname in dirs:
            subdir_path = os.path.join(current_dir, dirname)
            # The level for subdirectories depends on whether an index.adoc was present
            # If index.adoc was present, subdirectories are siblings to index.adoc, so same level as index.adoc.
            # If no index.adoc, subdirectories are normal children of the current folder.
            process_directory_recursive(subdir_path, level + 1)


    # Start the recursive process from the root directory at level 0
    process_directory_recursive(root_dir, 0)

    # Write the content to nav.adoc
    output_path = os.path.join(root_dir, "nav.adoc")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(nav_content))
        print(f"Successfully generated 'nav.adoc' in '{root_dir}' with hierarchical xref links (index.adoc aware).")
    except IOError as e:
        print(f"Error writing 'nav.adoc': {e}")

if __name__ == "__main__":
    input_directory = input("Enter the path to the directory you want to process: ")
    generate_nav_adoc(input_directory)