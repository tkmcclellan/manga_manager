import re


def clean_text(chapter_name):
    return re.sub(" +", " ", re.sub("\n", "", chapter_name)).strip()

def chapter_filename(chapter_name):
    return re.sub(' ', '-', re.sub('[^a-zA-Z0-9 ]', '', clean_text(chapter_name)))[:240] + ".pdf"
