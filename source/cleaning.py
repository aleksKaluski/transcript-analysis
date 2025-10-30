import os
import csv
import re
from pathlib import Path
import spacy
import pandas as pd


def tag_paragraph_with_spacy(doc):
    """
    Cleans unwanted spacy tags from a document and returns lemmas.
    :param doc: doc Spacy object
    :return: list of lemmas
    """
    clean_tokens = []

    for token in doc:
        if not (
                token.is_stop or
                token.is_punct or
                token.is_space or
                token.like_url or
                not token.is_alpha or
                len(token.text) <= 2
        ):
            clean_tokens.append(token.lemma_)
    return clean_tokens


def tag_csvfile_with_spacy(file_path: str, nlp: spacy.language.Language) -> pd.DataFrame:
    """
    Cleans unwanted spacy tags from a csv file and returns lemmas.
    :return: pandas.DataFrame
    """
    try:
        assert os.path.getsize(file_path) != 0
    except AssertionError:
        print(f"File {file_path} is empty!")

    print(f"Tagging {file_path}...")

    df = pd.read_csv(file_path, delimiter=';')
    # add clean text column for lemmas
    df['Clean Text'] = None

    # iterate though rows and make a clean representation
    for index, row in df.iterrows():

        # remove [niesłyszalne 00:00]
        clean = re.sub(r'\[[^\]]*\]', '', row[5])
        doc = nlp(clean)
        clean_tokens = tag_paragraph_with_spacy(doc)
        df.at[index, 'Clean Text'] = clean_tokens
    return df


def tag_folder_with_spacy(folder_path: str, nlp: spacy.language.Language) -> pd.DataFrame:
    """
    Cleans unwanted spacy tags from a folder and returns lemmas.
    :return: merged pandas.DataFrame
    """

    print('Tagging folder with spacy...\n')

    df = pd.DataFrame()
    for path, folders, files in os.walk(folder_path):
        # Open file
        for filename in files:
            if filename.endswith('.csv'):
                f = os.path.join(path, filename)
                df = pd.concat([df, tag_csvfile_with_spacy(f, nlp)])
    return df





