# DETA
This project contains the development made following SteelEye's Data Engineer Technical Assignment.

To set this project,you must follow this steps in order:
1. Run ```pip install poetry```
2. Run ```poetry install```

To run things using the poetry installed dependencies, you must use ```poetry run``` before:
- ```python script.py``` &rarr; ```poetry run python script.py```
- ```pytest tests``` &rarr; ```poetry run pytest tests```

This project is organized by 3 Classes:
- Downloader: reusable code for downloading from url's
- XMLHandler: code for treating xml data
- CSVHandler: code for treating csv data

### Running the project
The file deta/main.py serves as an integration test pipeline to run all the functionalities from end-to-end, 
and can be ran with the command ```poetry run python deta/main.py```

### Running Unit tests
To run the unit tests with coverage, simply run ```poetry run pytest --cov tests```.
These unit tests are also ran automatically using GitHub Actions once there is a Pull Request or 
a Push made to the main branch. This ensures that no untested or failing code is merged.

### Pre-commit checks
This project includes automated pre-commit hooks that help maintain code quality and consistency. These checks run automatically whenever you make a commit, and they include:

- black: Formats Python code to comply with PEP8 standards.
- ruff: Performs static code analysis for linting and style violations.
- mypy: Performs type checking based on function annotations.

These checks run automatically when a commit is done, but can be ran before with the command 
```poetry run pre-commit run```. This will automatically reformat the code to follow pep8 standards
and signal any failure needing improvements.