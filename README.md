# car

Create and activate a virtual environment
```python -m venv venv```

Install required packages in the environment
```pip install -r requirements.txt```

To try the models, run ```car/runner.py``` and select a model to run on the pre-existing grids.

Implementation of models can be found in ```car/models```, there are models for

- Resolution 1 Lazy Constraint
- Resolution 2 Lazy Constraint 
- Resolution 1 Flow Model
- Resolution 2 Flow Model

each model class takes as parameters a ```model_name```, a grid, and an entrance column.
