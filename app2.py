import os
import re
import json

def capitalize_first_letter(sentence):
    return sentence[0].upper() + sentence[1:] if sentence else sentence

def clean_question_text(raw_text):
    # Remove leading True: or False:
    raw_text = re.sub(r'^(True|False)\s*:\s*', '', raw_text, flags=re.IGNORECASE)

    # Remove "It is true that"/"It is false that"
    raw_text = re.sub(r'^(It is (true|false) that\s*)', '', raw_text, flags=re.IGNORECASE)

    # Remove trailing "and it is true/false."
    raw_text = re.sub(r'(\s*and it is (true|false)\.)$', '', raw_text, flags=re.IGNORECASE)

    return raw_text.strip()

def parse_true_false(text):
    results = []
    seen_questions = set()
    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Format: "54. It is false that... (True)"
        match_1 = re.match(r'^(\d+)\.\s+(.*)\s+\((True|False)\)', line, re.IGNORECASE)

        # Format: "19. True: The geese flew away..."
        match_2 = re.match(r'^(\d+)\.\s*(True|False)\s*:\s*(.+)', line, re.IGNORECASE)

        # Format: "12. It is true that..." or "11. ... and it is false."
        match_3 = re.match(r'^(\d+)\.\s+(.*)', line)

        question_text = None
        answer_bool = None

        if match_1:
            question_text = clean_question_text(match_1.group(2).strip())
            answer_bool = match_1.group(3).lower() == 'true'

        elif match_2:
            question_text = clean_question_text(match_2.group(3).strip())
            answer_bool = match_2.group(2).lower() == 'true'

        elif match_3:
            raw_q = match_3.group(2).strip()
            lower_q = raw_q.lower()
            if ' it is true' in lower_q or lower_q.startswith('it is true') or lower_q.endswith('it is true')  or lower_q.startswith('true:'):
                answer_bool = True
            elif ' it is false' in lower_q or lower_q.startswith('it is false') or lower_q.endswith('it is false')  or lower_q.startswith('false:'):
                answer_bool = False
            else:
                continue  # Not a clear true/false statement
            question_text = clean_question_text(raw_q)

        if question_text and question_text.lower() not in seen_questions:
            seen_questions.add(question_text.lower())
            results.append({
                "id": len(results) + 1,
                "question": capitalize_first_letter(question_text),
                "answer": answer_bool
            })

    return json.dumps(results, indent=2, ensure_ascii=False)


def parse_short_long_answer_to_file(text):
    pattern = re.compile(
    r'^(\d+)\.\s+(?:Question:\s*)?(.*?)\n\s*(?:-*\s*Answer\s*:)\s*(.+?)$', 
    re.DOTALL | re.MULTILINE
)
    results = []

    matches = pattern.findall(text)
    seen_questions = set()

    for idx, (qid, question, answer) in enumerate(matches):
        question_clean = question.strip()
        answer_clean = answer.strip()

        if question_clean.lower() in seen_questions:
            continue
        seen_questions.add(question_clean.lower())

        results.append({
            "id": len(results) + 1,
            "question": capitalize_first_letter(question_clean),
            "answer": answer_clean
        })
    
    json_string = json.dumps(results, indent=2)
    return json_string

def parse_fb_quiz(text):
    pattern = re.compile(
        r'^(\d+)\.\s+(.*?)\n\s*[Aa][\.\)]\s+(.*?)\n\s*[Bb][\.\)]\s+(.*?)\n\s*[Cc][\.\)]\s+(.*?)\n\s*[Dd][\.\)]\s+(.*?)\n\s*(?:Correct Answer:|Answer:)\s*([A-Da-d])[\)\.]?',
        re.MULTILINE | re.DOTALL
    )

    results = []
    seen_questions = set()

    matches = pattern.findall(text)
    for match in matches:
        question = match[1].strip()
        options = [match[2].strip(), match[3].strip(), match[4].strip(), match[5].strip()]
        answer_letter = match[6].strip().upper()
        answer_index = ['A', 'B', 'C', 'D'].index(answer_letter)

        if question.lower() in seen_questions:
            continue
        seen_questions.add(question.lower())

        results.append({
            "id": len(results) + 1,
            "question": capitalize_first_letter(question),
            "options": capitalize_first_letter(options),
            "answer": answer_index
        })

    json_string = json.dumps(results, indent=2, ensure_ascii=False)
    return json_string

def process_section_files(section_folder):
    for root, _, files in os.walk(section_folder):
        for file in files:
            if file.endswith('True_False.txt'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                if file.endswith('True_False.txt'):
                    response = parse_true_false(text)
                elif file.endswith('Short_Answer.txt'):
                    response = parse_short_long_answer_to_file(text)
                elif file.endswith('Long_Answer.txt'):
                    response = parse_short_long_answer_to_file(text)
                elif file.endswith('Quiz.txt'):
                    response = parse_fb_quiz(text)
                elif file.endswith('Fill_in_the_blanks.txt'):
                    response = parse_fb_quiz(text)

                json_filename = os.path.splitext(file_path)[0] + ".json"

                try:
                    # First try loading raw JSON
                    parsed = json.loads(response)

                    # # Now validate against schema
                    # validated = QuestionSet(**parsed)

                    with open(json_filename, 'w', encoding='utf-8') as json_file:
                        json.dump(parsed, json_file, indent=2)

                except json.JSONDecodeError as e:
                    print(f"❌ Failed to decode JSON for {file_path}")
                    print("⚠️ Raw response:", response)
                    print("Error:", e)

                except Exception as e:
                    print(f"❌ Schema validation failed for {file_path}")
                    print("⚠️ Raw response:", response)
                    print("Error:", e)
                    

# process_section_files('NCERT-5th-English-part 1_chapters/NCERT-5th-English-part 1-chapter1-Ice_cream_Man')
# process_section_files('NCERT-5th-English-part 1_chapters/NCERT-5th-English-part 1-chapter2-Wonderful_Waste')
# process_section_files("NCERT-5th-English-part 1_chapters/NCERT-5th-English-part 1-chapter3-Teamwork")
# process_section_files("NCERT-5th-English-part 1_chapters/NCERT-5th-English-part 1-chapter4-Flying_Together")
# process_section_files("NCERT-5th-English-part 1_chapters/NCERT-5th-English-part 1-chapter5-My_Shadow")
# process_section_files("NCERT-5th-English-part 1_chapters/NCERT-5th-English-part 1-chapter6-Robinson_Crusoe_Discovers_a_Footprint")
# process_section_files("NCERT-5th-English-part 1_chapters/NCERT-5th-English-part 1-chapter7-Crying")
process_section_files("NCERT-5th-English-part 1_chapters/NCERT-5th-English-part 1-chapter8-My_Elder_Brother")

