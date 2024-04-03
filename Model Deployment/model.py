# FastAPI: https://betterdatascience.com/deploy-a-machine-learning-model-with-fastapi/
# Docker: https://dev.to/code_jedi/machine-learning-model-deployment-with-fastapi-and-docker-llo
# Docs: https://dorian599.medium.com/ml-deploy-machine-learning-models-using-fastapi-6ab6aef7e777

# Libraries
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from pydantic import BaseModel
from sklearn import datasets
import joblib

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

iris = datasets.load_iris()

# Schema: Form Validation
class IrisSpecies(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


# Model: Training | Prediction 
class IrisModel:
    """Class constructor will loads the dataset and model
    If not, trains the model and save it"""
    def __init__(self):
        self.df = pd.DataFrame(np.column_stack((iris.data, iris.target)), columns=iris.feature_names + ['Species']).astype({'Species':int})
        print(f"Dataset Features: {self.df.columns.to_list()}\nDataset Shape: {self.df.shape}")
        print("First 2 Records: \n", self.df.head(2))
        self.df.info(memory_usage='deep')
        # self.df.Species.replace({index: value for index, value in enumerate(iris.target_names)}, inplace=True)

        # Pickle file
        """
        try:
            self._model_loc = './model.pkl'
            self._model = joblib.load(self._model_loc)
            self._model = self._train_model()
            joblib.dump(self._model, self._model_loc)
        except Exception as _:
            self._model = self._train_model()
            joblib.dump(self._model, self._model_loc)
        """

        # Joblib file
        try:
            self.joblib_in = open('./model.joblib', '+wb')
            self._model = joblib.load(self.joblib_in)
            self._model = self._train_model()
            joblib.dump(self._model, self.joblib_in)
        except Exception as _:
            self._model = self._train_model()
            joblib.dump(self._model, self.joblib_in)
            

    # Training the model
    def _train_model(self):
        x = self.df.drop('Species', axis=1)
        y = self.df['Species']
        rfc = RandomForestClassifier()
        model = rfc.fit(x,y)
        return model
    
    # Prediction 
    def predict_species(self, sepal_length, sepal_width, petal_length, petal_width):
        data_in = [[sepal_length, sepal_width, petal_length, petal_width]]
        prediction = self._model.predict(data_in).tolist()
        probability = self._model.predict_proba(data_in).max()
        return {index: value for index, value in enumerate(iris.target_names)}[prediction[0]], probability