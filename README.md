# Cantonese Flashcard Learning Application

A PyQt5-based flashcard application for learning Cantonese vocabulary with interactive quizzes.

## Features

- **Interactive Flashcards**: Learn Cantonese characters, Jyutping romanization, and English translations
- **Type-Based Filtering**: Filter cards by category (Pronouns, Basics, Numbers, Verbs, Adjectives, etc.)
- **Progress Tracking**: Track correct and incorrect answers for each word
- **Multiple Quiz Modes**: 
  - Character recognition (given English, guess character)
  - Jyutping (given English, guess Jyutping)
  - English translation (given character or Jyutping, guess English)
- **CSV Data Management**: Load and save flashcard data in CSV format

## Requirements

- Python 3.8.1+
- PyQt5 5.15+

## Installation

### Using Poetry
```bash
poetry install
```


## Usage

### Run the Application

With Poetry:
```bash
poetry run python flashcard.py
```

Or directly:
```bash
python flashcard.py [CSV_FILE]
```

### CSV Format

The CSV file should have the following columns:
- `Word`: Cantonese character
- `Jyutping`: Romanization of Cantonese
- `English`: English translation
- `Questioned`: Number of times questioned (auto-tracked)
- `Correct`: Number of correct answers (auto-tracked)
- `Type`: Category/Type of the word

Example:
```
Word,Jyutping,English,Questioned,Correct,Type
我,ngo5,I/ME,2,1,Pronouns
你,nei5,YOU,4,4,Pronouns
唔,m4,NOT,2,2,Basics
```

## Development

### Install Dev Dependencies

```bash
poetry install
```

### Run Tests

```bash
poetry run pytest
```

## License

MIT
