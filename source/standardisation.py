from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
import csv
import re
from pathlib import Path
import shutil
from num2words import num2words
import spacy


def delete_folder_content(folder_path: str):
    # delete the content of the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def create_file_name(file, PDF=False, TXT=False):
    p = Path(file)
    file_name = p.name
    file_name = file_name.replace('.mp4', '')
    if PDF:
        return file_name.replace('.txt', '.pdf')
    elif TXT:
        return file_name.replace('.csv', '.txt')
    else:
        return file_name.replace('.csv', '_stan.csv')


def check_if_empty(path: str) -> bool:
    return len(os.listdir(path)) == 0


def replace_numbers_with_words(nlp, input_text: str) -> str:
    assert isinstance(input_text, str); f"you passed sth which is not a word to the tokenizer!"
    doc = nlp(input_text)

    new_tokens = []
    for token in doc:
        if token.pos_ == "NUM":
            # convert
            try:
                n = int(token.text)
                word = num2words(n, lang='pl')
                print(f"{token.text} -> {word}")
                new_tokens.append(word)
            except ValueError:
                new_tokens.append(token.text)
        else:
            new_tokens.append(token.text)

    new_text = " ".join(new_tokens)

    # Remove spaces before punctuation
    new_text = re.sub(r"\s+([,!.?:;)\]])", r"\1", new_text)

    # Remove spaces after opening brackets or quotes (including typographic ones)
    new_text = re.sub(r"([(\[\"'„‘])\s+", r"\1", new_text)

    # Remove spaces before closing brackets or quotes (including typographic ones)
    new_text = re.sub(r"\s+([\"'\])”’])", r"\1", new_text)

    # Collapse excessive newlines and spaces
    new_text = re.sub(r"\s*\n+\s*", " ", new_text)
    new_text = re.sub(r"\s{2,}", " ", new_text)
    return new_text


def replace_unwanted_signs(csv_file, new_csv_file):
    nlp = spacy.load("pl_core_news_sm")
    with open(csv_file, "r", encoding='utf-8', newline='') as source, \
            open(new_csv_file, "w", encoding='utf-8', newline='') as target:
        # print(f"input file: {csv_file}")

        try:
            assert os.path.getsize(csv_file) != 0
        except AssertionError:
            print(f"File {csv_file} is empty!")

        # print(f"output file: {new_csv_file}")

        csv_reader = csv.reader(source, delimiter=';')
        csv_writer = csv.writer(target, delimiter=';')
        nonword_regex = r'nonword|\[niesłyszalne \d{1,2}:\d{1,2}:\d{1,2}\]'

        count = 0  # count replaced words
        changed_words = []

        loops = 0 # purely informative
        for lines in csv_reader:
            if len(lines) > 5:
                original_text = lines[5]
                start_time = lines[2]
                formatted_time = ':'.join(start_time.split(':')[:2])
                inaudible = "[niesłyszalne " + formatted_time + "]"

                changed_words.append(re.findall(nonword_regex, original_text))
                new_text = re.sub(nonword_regex, inaudible, original_text, flags=re.IGNORECASE)

                if new_text != original_text:
                    count += 1
                    # print(f"Old: {original_text}")
                    # print(f"New: {new_text}")
                    lines[5] = new_text

                # Basic replacements
                # currency
                lines[5] = re.sub(r"\bPLN\b", "złotych", lines[5], flags=re.IGNORECASE)
                lines[5] = re.sub(r"\bzł\b", "złotych", lines[5], flags=re.IGNORECASE)

                # Z%
                lines[5] = re.sub(r"100%", "sto procent", lines[5])

                # names
                lines[1] = re.sub(r"\bProwadząca\b", "Ada", lines[1], flags=re.IGNORECASE)

                # speaker names
                lines[1] = re.sub(r"\bPan\b", "", lines[1], flags=re.IGNORECASE)
                lines[1] = re.sub(r"\bPani\b", "", lines[1], flags=re.IGNORECASE)

                # delete '
                lines[5] = re.sub(r"['’]", "", lines[5])

                def match_okej_case(match):
                    text = match.group()
                    base = 'okej'
                    if text.isupper():  # "OK" → "OKEJ"
                        return base.upper()
                    elif text[0].isupper():  # "Ok" → "Okej"
                        return base.capitalize()
                    else:  # "ok" → "okej"
                        return base

                lines[5] = re.sub(r"\bok[,.]?\b", match_okej_case, lines[5], flags=re.IGNORECASE)

                # Convert numbers to words
                lines[5] = replace_numbers_with_words(nlp=nlp, input_text=lines[5])

                csv_writer.writerow(lines)

            else:
                print(f"Skipped {lines}")

        print(f'{count} words replaced!\n')
        # print(f"The words: {changed_words.remove([])}")


def export_csv_to_txt(input_file, output_file):
    with open(input_file, "r", encoding='utf-8') as source, open(output_file, "w", encoding='utf-8') as target:
        csv_reader = csv.reader(source, delimiter=';')
        next(csv_reader)
        for lines in csv_reader:
            if len(lines) > 5:
                target.write(lines[0] + ") " + lines[1] + " (" + lines[2] + ")")
                target.write('\n')
                target.write(lines[5])
                target.write('\n')
                target.write('\n')


def standardise(input_folder, output_folder):
    print('\nStandardising...')
    os.makedirs(output_folder, exist_ok=True)  # create folder if it does not exist
    delete_folder_content(output_folder)
    for path, folders, files in os.walk(input_folder):
        # Open file
        for filename in files:
            # print(filename)
            if filename.endswith('.csv'):
                f = os.path.join(path, filename)
                replace_unwanted_signs(f, os.path.join(output_folder, create_file_name(f, PDF=False, TXT=False)))


def export_folder_to_txt(input_folder, output_folder):
    print('Exporting to TXT...\n')
    os.makedirs(output_folder, exist_ok=True)
    delete_folder_content(output_folder)


    for path, folders, files in os.walk(input_folder):

        # Open file
        for filename in files:
            # print(filename)
            if filename.endswith('.csv'):
                f = os.path.join(path, filename)
                export_csv_to_txt(f, os.path.join(output_folder, create_file_name(f, PDF=False, TXT=True)))


def txt_to_pdf(txt_path, pdf_path):

    # creat output folder
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    # font with Polish diacritics
    font_path = "files/fonts/DejaVuSans.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError(
            f"Font file '{font_path}' not found! "
        )

    pdfmetrics.registerFont(TTFont("RobotoMonoLight", font_path))
    pdfmetrics.registerFont(TTFont("RobotoMonoBold", r"files/fonts/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("RobotoMonoRegular", r"files/fonts/DejaVuSans.ttf"))

    # title
    filename = os.path.basename(txt_path).replace(".txt", "").replace(".pdf", "")
    parts = filename.split("_")
    name = parts[0].upper()
    number = parts[1]

    if number == 'w1':
        number = 'Wywiad I'
    elif number == 'w2':
        number = 'Wywiad II'
    elif number == 'w3':
        number = 'Wywiad III'

    date = parts[3]

    pretty_title = name + " | " + number + " (" + date + ")"


    # Metadata setup
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=3 * cm,
        bottomMargin=2 * cm,
        title=os.path.basename(txt_path).replace(".txt", ""),
        author="Transcription Processor",
        subject="Text-to-PDF Conversion",
        creator="Python ReportLab"
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Speaker',
                              fontName='RobotoMonoRegular',
                              fontSize=12,
                              leading=14,
                              spaceAfter=10,
                              textColor='#080808'))

    styles.add(ParagraphStyle(name='Text',
                              fontName='RobotoMonoLight',
                              fontSize=10,
                              leading=15,
                              spaceAfter=12))
    elements = []

    # Read input text
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # Split by blocks (0) X (time)\nText)
    blocks = re.split(r"\n(?=\d+\)\s)", content)

    for block in blocks:
        match = re.match(r"(\d+)\)\s*(.*?)\s*\((.*?)\)\n(.*)", block, re.S)
        if match:
            number, speaker, time, text = match.groups()
            speaker_line = f"<b>{speaker}</b> [{time}]"
            body_text = text.strip().replace("\n", " ")
            elements.append(Paragraph(speaker_line, styles['Speaker']))
            elements.append(Paragraph(body_text, styles['Text']))
            elements.append(Spacer(1, 10))

    # Function to add page numbers
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"{page_num}"
        canvas.setFont("RobotoMonoRegular", 9)
        canvas.drawCentredString(A4[0] / 2.0, 1 * cm, text)

    def add_title_and_number(canvas, doc):
        canvas.setFont("RobotoMonoBold", 16)
        canvas.drawCentredString(A4[0] / 2.0, A4[1] - 2 * cm, pretty_title)
        add_page_number(canvas, doc)

    doc.build(elements, onFirstPage=add_title_and_number, onLaterPages=add_page_number)

    print(f"PDF successfully created: {pdf_path}")


def export_folder_to_pdf(input_folder, output_folder):
    print('\nExporting to PDF...')
    assert os.path.exists(input_folder);
    f"input folder ({input_folder}) does not exist!"


    os.makedirs(output_folder, exist_ok=True)
    # print(f"input folder: {input_folder}")
    # print(f"output folder: {output_folder}")

    def is_valid_filename(filename):
        pattern = r"^[A-Z]{3}_w\d+_video_\d{2}\.\d{2}\.\d{4}_[a-z]+\.txt$"
        return bool(re.match(pattern, filename))

    # clean the folder to minimize the amout of reduntent data
    delete_folder_content(output_folder)
    for path, folders, files in os.walk(input_folder):
        if check_if_empty(input_folder):
            print(f"[!] input folder {input_folder} is empty!")

        # Open file
        for filename in files:

            if not is_valid_filename(filename):
                print(f"[!] invalid filename {filename}! - skipped")
                continue
            elif filename.endswith('.txt'):
                f = os.path.join(path, filename)
                txt_to_pdf(f, os.path.join(output_folder, create_file_name(f, PDF=True, TXT=False)))

    if check_if_empty(output_folder):
        print(f"[!] output folder {output_folder} is empty!")
    else:
        print(f"\nSucessfull PDF conversion!")


