from phonemizer import phonemize

def phonemizeText(text):
    """
    Phonemize the given text
    Args:
        text (str): the text to be phonemized
    Returns:
        phonemes (str): the phonemized text
    """
    phonemes = phonemize(text=text)
    return phonemes