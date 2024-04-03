from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi import File, UploadFile
from io import BytesIO

from typing import Dict
import uvicorn

from model import IrisSpecies, IrisModel
import pandas as pd
import joblib

import warnings 
warnings.filterwarnings('ignore')


app = FastAPI()
model = IrisModel()

app.mount("/static", StaticFiles(directory="static", html = True), name="static")

@app.get('/', response_class=HTMLResponse)
def index():
    return "Hello World!"

@app.get('/data')
def get_data():
    return model.df.to_dict()

# Link: https://stackoverflow.com/questions/65342833/fastapi-uploadfile-is-slow-compared-to-flask/70667530#70667530
# Link: https://stackoverflow.com/questions/63048825/how-to-upload-file-using-fastapi
"""
# Link: https://stackoverflow.com/questions/6081008/dump-a-numpy-array-into-a-csv-file
random_species = lambda n: np.column_stack(((np.random.rand(n,4) * 0.5).round(1), np.random.randint(0,3, n)))
np.savetxt('Model Deployment\iris.csv', np.array(random_species(50)), delimiter=',', fmt='%0.1f')
"""
@app.post('/upload')
async def upload(file: UploadFile = File(...)):
    try:
        data = pd.read_csv(BytesIO(file.file.read()), header=None).astype({4:int})
        data.columns = model.df.columns
        print(f"Previous df size: {model.df.shape[0]}")
        model.df = pd.concat([model.df, data], ignore_index=True)
        print(f"After upload df size: {model.df.shape[0]}")
    except Exception as e:  
        return {"message": f"There was a error while uploading the file with the error: {e}"}
    finally:
        await file.close()
    return {"message": f"Successfully uploaded {file.filename}"}

@app.get('/train')
def train_model():
    # Joblib file
    try:
        joblib_in = open('./model.joblib', 'rb')
        model._model = joblib.load(joblib_in)
        model._model = model._train_model()
        joblib.dump(model._model, joblib_in)
    except Exception as _:
        model._model = model._train_model()
        joblib.dump(model._model, joblib_in)
    finally:
        return f"Model Trained Successfully with df size: {model.df.shape[0]}"

@app.post('/predict')
def predictions(iris: IrisSpecies):
    data = iris.model_dump()
    prediction, probability = model.predict_species(
        data["sepal_length"], data["sepal_width"], data["petal_length"], data["petal_width"]
    )
    return {'Prediction': prediction, "Probability": probability}


if __name__ == '__main__':
    uvicorn.run(app, debug=True, host='127.0.0.1', port=8000)