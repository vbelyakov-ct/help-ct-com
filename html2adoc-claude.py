#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import tempfile
import subprocess
from bs4 import BeautifulSoup

def select_folder():
    """Prompts the user for the path to the folder with HTML files through the console."""
    print("Enter the full path to the folder containing HTML files:")
    folder_path = input("> ").strip()
    
    # Check if the specified folder exists
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        print("The specified path does not exist or is not a folder.")
        return None
    
    return folder_path

def create_output_folder(input_folder):
    """Creates a folder for output files."""
    output_folder = os.path.join(input_folder, "adoc_output")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    return output_folder

def check_pandoc_installed():
    """Checks if pandoc is installed in the system."""
    try:
        subprocess.run(["pandoc", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        print("Error: pandoc is not installed or not found in the system path.")
        print("Please install pandoc: https://pandoc.org/installing.html")
        return False

def extract_title(html_content):
    """Extract title from HTML content."""
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
    if title_match:
        return title_match.group(1).strip()
    
    # Try with BeautifulSoup if regex fails
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            return title_tag.string.strip()
    except:
        pass
    
    return None

def process_html_file(input_path, output_path):
    """Process single HTML file to AsciiDoc."""
    try:
        print(f"Processing file: {os.path.basename(input_path)}")
        
        # Read the HTML file
        with open(input_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Extract title from the HTML
        title = extract_title(html_content)
        
        # 1. Process <span class="confluence-information-macro-*"> (TIP, NOTE, WARNING, INFO)
        for info_class, adoc_type in {
            'confluence-information-macro-tip': 'TIP',
            'confluence-information-macro-note': 'NOTE',
            'confluence-information-macro-warning': 'WARNING',
            'confluence-information-macro-info': 'INFO'
        }.items():
            # Find all such spans
            pattern = re.compile(f'<span\\s+class="{info_class}"[^>]*>(.*?)</span>', re.DOTALL)
            
            def info_block_replace(match):
                content = match.group(1)
                # Process nested object spans
                obj_pattern = re.compile(r'<span\s+class="object"[^>]*>(.*?)</span>', re.DOTALL)
                content = obj_pattern.sub(r'[.object]#\1#', content)
                # Process nested apiobject spans
                apiobj_pattern = re.compile(r'<span\s+class="apiobject"[^>]*>(.*?)</span>', re.DOTALL)
                content = apiobj_pattern.sub(r'[.apiobject]#\1#', content)
                # Create properly formatted block with TWO newlines after closing ====
                return f"[{adoc_type}]\n====\n{content}\n====\n\n"
            
            html_content = pattern.sub(info_block_replace, html_content)
        
        # 2. Process <span class="apiobject"> tags
        apiobject_pattern = re.compile(r'<span\s+class="apiobject"[^>]*>(.*?)</span>', re.DOTALL)
        html_content = apiobject_pattern.sub(r'[.apiobject]#\1#', html_content)
        
        # 3. Process remaining <span class="object"> tags
        object_pattern = re.compile(r'<span\s+class="object"[^>]*>(.*?)</span>', re.DOTALL)
        html_content = object_pattern.sub(r'[.object]#\1#', html_content)
        
        # 4. Process <ch:include tags="ios,win"> to ifdef::ios,win[]
        include_pattern = re.compile(r'<ch:include\s+tags="([^"]*)"[^>]*>')
        html_content = include_pattern.sub(r'ifdef::\1[]', html_content)
        
        # 5. Process <ch:exclude tags="kotlin"> to ifndef::kotlin[]
        exclude_pattern = re.compile(r'<ch:exclude\s+tags="([^"]*)"[^>]*>')
        html_content = exclude_pattern.sub(r'ifndef::\1[]', html_content)
        
        # 6. Process collapsible sections
        # Original toggleBox version
        collapsible_pattern = re.compile(r'<div\s+class="showMoreLabel\s+nonPrintable"\s+onclick="toggleBox\(this\)"[^>]*>(.*?)</div>', re.DOTALL)
        html_content = collapsible_pattern.sub(r'.Click to view\n[%collapsible]\n====\n\1\n====\n\n', html_content)
        
        # New hidden block version (hideLabel/showMoreContent structure)
        hidden_block_pattern = re.compile(r'<div\s+class="hideLabel\s+Article_hiddenBlock\s+nonPrintable"[^>]*?onclick="toggleBox\(this\)"[^>]*>(.*?)</div>\s*<div\s+class="showMoreContent\s+Article_hiddenBlock"[^>]*>(.*?)</div>', re.DOTALL)
        
        def hidden_block_replace(match):
            label = match.group(1).strip()
            content = match.group(2).strip()
            
            # Extract "Click to hide" or any text label
            label_text = re.sub(r'<[^>]+>', '', label).strip()
            if not label_text:
                label_text = "Click to view"
                
            return f".{label_text}\n[%collapsible]\n====\n{content}\n====\n\n"
            
        html_content = hidden_block_pattern.sub(hidden_block_replace, html_content)
        
        # 7. Process <ch:codeSample> to [source]
        code_pattern = re.compile(r'<ch:codeSample[^>]*>(.*?)</ch:codeSample>', re.DOTALL)
        html_content = code_pattern.sub(r'[source]\n----\n\1\n----\n\n', html_content)
        
        # 8. Process <ch:nav type="minitoc" maxLevel="3"> to :toc: :toclevels: 3
        nav_pattern = re.compile(r'<ch:nav\s+type="minitoc"\s+maxLevel="(\d)"[^>]*>')
        html_content = nav_pattern.sub(r':toc: \n:toclevels: \1', html_content)
        
        # Write the preprocessed content to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', encoding='utf-8', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(html_content)
        
        # Convert to AsciiDoc with pandoc
        try:
            subprocess.run(
                ['pandoc', '-f', 'html', '-t', 'asciidoc', temp_file_path, '-o', output_path],
                check=True
            )
            
            # Add title to the beginning of the AsciiDoc file
            if title:
                with open(output_path, 'r', encoding='utf-8') as file:
                    adoc_content = file.read()
                
                # Add title at the beginning of the file with proper AsciiDoc format
                adoc_content = f"= {title}\n\n{adoc_content}"
                
                with open(output_path, 'w', encoding='utf-8') as file:
                    file.write(adoc_content)
            
            print(f"Successfully converted: {os.path.basename(input_path)}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error during pandoc conversion: {e}")
            return False
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        print(f"Error processing file {os.path.basename(input_path)}: {e}")
        import traceback
        traceback.print_exc()
        return False

def post_process_files(output_folder):
    """Apply post-processing to all converted files."""
    for filename in os.listdir(output_folder):
        if filename.endswith('.adoc'):
            file_path = os.path.join(output_folder, filename)
            
            try:
                # Read the file
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # 1. Fix broken object and apiobject tags with line breaks
                object_pattern = re.compile(r'\[\.object\]#(.*?)(\n+.*?)#', re.DOTALL)
                apiobject_pattern = re.compile(r'\[\.apiobject\]#(.*?)(\n+.*?)#', re.DOTALL)
                
                def fix_tags(match):
                    content = match.group(1).strip() + ' ' + match.group(2).strip()
                    content = re.sub(r'\s+', ' ', content)
                    return f'{match.group(0).split("#")[0]}#{content}#'
                
                content = object_pattern.sub(fix_tags, content)
                content = apiobject_pattern.sub(fix_tags, content)
                
                # 2. Fix broken admonition blocks where opening and closing are separated
                for block_type in ['TIP', 'NOTE', 'WARNING', 'INFO']:
                    # Pattern to match a block that's cut off
                    pattern = re.compile(f'\\[{block_type}\\]\\s*\n*====\\s*(.*?)\\s*====\\s*\n+(.*?)(?=\\[|\\d+\\.|\\*|\\+\\s+image:../../../../images/|$)', re.DOTALL)
                    
                    def fix_split_block(match):
                        inside_content = match.group(1).strip()
                        after_content = match.group(2).strip() if match.group(2) else ""
                        
                        # Check if the after content seems to be a continuation
                        if after_content and not (re.match(r'^(\d+\.|\*|\+\s+image:../../../../images/)', after_content) or 
                                                 re.search(r'\[(?:TIP|NOTE|WARNING|INFO)\]', after_content)):
                            # Check if after_content is likely a list item or a new paragraph
                            if re.match(r'^\d+\.', after_content) or after_content.startswith('*') or '+' in after_content[:10]:
                                # This is likely a list item or image, don't include it
                                inside_content = re.sub(r'\s+', ' ', inside_content)
                                result = f"[{block_type}]\n====\n{inside_content}\n====\n\n{after_content}\n\n"
                                return result
                            else:
                                # This is likely a continuation of the block content
                                full_content = inside_content + " " + after_content
                                full_content = re.sub(r'\s+', ' ', full_content)
                                return f"[{block_type}]\n====\n{full_content}\n====\n\n"
                        else:
                            # Just fix the formatting of the block itself
                            inside_content = re.sub(r'\s+', ' ', inside_content)
                            result = f"[{block_type}]\n====\n{inside_content}\n====\n\n"
                            if after_content:
                                result += after_content + "\n\n"
                            return result
                    
                    content = pattern.sub(fix_split_block, content)
                    
                    # Ensure all admonition blocks have proper formatting and two newlines after closing ====
                    pattern = re.compile(f'\\[{block_type}\\]\\s*\n*====\\s*(.*?)\\s*====', re.DOTALL)
                    
                    def ensure_proper_format(match):
                        block_content = match.group(1).strip()
                        block_content = re.sub(r'\s+', ' ', block_content)
                        return f"[{block_type}]\n====\n{block_content}\n====\n\n"
                    
                    content = pattern.sub(ensure_proper_format, content)
                
                # 3. Fix any remaining ADOC_MARKER_* that might be in the text
                pattern = re.compile(r'ADOC_MARKER_[A-Z]+_\d+_\d+')
                for marker_match in pattern.finditer(content):
                    marker = marker_match.group(0)
                    if 'TIP' in marker:
                        content = content.replace(marker, "[TIP]\n====\nThis content had a conversion issue.\n====\n\n")
                    elif 'NOTE' in marker:
                        content = content.replace(marker, "[NOTE]\n====\nThis content had a conversion issue.\n====\n\n")
                    elif 'WARNING' in marker:
                        content = content.replace(marker, "[WARNING]\n====\nThis content had a conversion issue.\n====\n\n")
                    elif 'INFO' in marker:
                        content = content.replace(marker, "[INFO]\n====\nThis content had a conversion issue.\n====\n\n")
                    else:
                        content = content.replace(marker, "")
                
                # 4. Make a final pass to ensure ALL admonition blocks have two newlines after closing ====
                for block_type in ['TIP', 'NOTE', 'WARNING', 'INFO']:
                    # Replace single newline after ==== with two newlines
                    content = re.sub(f'\\[{block_type}\\]\\s*\n*====\\s*(.*?)\\s*====\\s*\n', 
                                    f"[{block_type}]\n====\n\\1\n====\n\n", content, flags=re.DOTALL)
                
                # Write the fixed content back
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                    
            except Exception as e:
                print(f"Error post-processing file {filename}: {e}")
                import traceback
                traceback.print_exc()

def process_files(input_folder, output_folder):
    """Process all HTML files in the specified folder."""
    files_processed = 0
    
    for filename in os.listdir(input_folder):
        if filename.endswith('.html'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename.replace('.html', '.adoc'))
            
            if process_html_file(input_path, output_path):
                files_processed += 1
    
    return files_processed

def main():
    print("HTML to AsciiDoc Converter")
    print("-------------------------")
    
    # Check if pandoc is installed
    if not check_pandoc_installed():
        return
    
    # Request folder path from user via console
    input_folder = select_folder()
    if not input_folder:
        print("Folder not selected or incorrectly specified. Terminating.")
        return
    
    # Create folder for output files
    output_folder = create_output_folder(input_folder)
    
    # Process files
    files_processed = process_files(input_folder, output_folder)
    
    # Apply post-processing
    print("Applying post-processing to fix any remaining issues...")
    post_process_files(output_folder)
    
    print(f"\nProcessing complete. Files processed: {files_processed}")
    print(f"Results saved in: {output_folder}")

if __name__ == "__main__":
    main()