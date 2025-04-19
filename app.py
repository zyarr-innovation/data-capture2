import os
import re

def split_chapters(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match chapters
    pattern = re.compile(r'(Chapter\s+\d+\s*:\s*.*?)(?=Chapter\s+\d+\s*:|$)', re.DOTALL | re.IGNORECASE)
    matches = pattern.findall(content)

    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    output_dir = f"{base_filename}_chapters"
    os.makedirs(output_dir, exist_ok=True)

    for match in matches:
        header_match = re.match(r'Chapter\s+(\d+)\s*:\s*(.*)', match, re.IGNORECASE)
        if header_match:
            chapter_number = header_match.group(1).strip()
            chapter_title = header_match.group(2).strip().replace(' ', '_')
            filename = f"{base_filename}-chapter{chapter_number}-{chapter_title}.txt"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as out_file:
                out_file.write(match.strip())


def split_sections_in_chapters(chapter_folder):
    for file_name in os.listdir(chapter_folder):
        if file_name.endswith('.txt'):
            file_path = os.path.join(chapter_folder, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            base_name = os.path.splitext(file_name)[0]
            chapter_dir = os.path.join(chapter_folder, base_name)
            os.makedirs(chapter_dir, exist_ok=True)

            pattern = re.compile(r'(Section\s*:\s*.*?)(?=Section\s*:|$)', re.DOTALL | re.IGNORECASE)
            sections = pattern.findall(content)

            chapter_info_match = re.match(r'^(.*?)-chapter(\d+)-(.+)$', base_name)
            if not chapter_info_match:
                continue
            base_filename = chapter_info_match.group(1)
            chapter_number = chapter_info_match.group(2)
            chapter_title = chapter_info_match.group(3)

            for section in sections:
                section_header_match = re.match(r'Section\s*:\s*(.*)', section, re.IGNORECASE)
                if not section_header_match:
                    continue
                section_title = section_header_match.group(1).strip().replace(' ', '_')
                section_filename = f"{base_filename}-chapter{chapter_number}-{chapter_title}-{section_title}.txt"
                section_path = os.path.join(chapter_dir, section_filename)
                with open(section_path, 'w', encoding='utf-8') as sec_file:
                    sec_file.write(section.strip())


# Example usage
#split_chapters('NCERT-5th-English-part 1.txt')
split_sections_in_chapters('NCERT-5th-English-part 1_chapters')