# IS 601 - Module 5: Assignment-Interactive Calculator Command-Line
References: https://github.com/kaw393939/module5_is601

## To Run
```bash
python main.py
```

## To Test
```bash
coverage run -m pytest && coverage report
```
or
```bash
pytest
```

If you are coding on a remote server like I do, a `.coveragrc` file may be needed to allow for the data file to be generated correctly.  
Example .coveragrc file:
```
[run]
data_file = /tmp/.coverage
```

## Notes
Python automatically creates bytecode cache files in the \_\_pycache\_\_ folder. However, these files cause unit tests like coverage and pytest to not update. To remove \_\_pycache\_\_ folders:  
```bash
find . -type d -name "__pycache__" -exec rm -r {} +
```