clone the repository

# install requirements
pip install -r requirements.txt

# run code
python main.py

# APIs

1.  http://127.0.0.1:8080/data/?well=<well api number>
  returns the sum of productions
  example:
  http://127.0.0.1:8080/data/?well=34167297250000 
  returns
  {
    "brine": 1724,
    "gas": 37125,
    "oil": 797
  }
