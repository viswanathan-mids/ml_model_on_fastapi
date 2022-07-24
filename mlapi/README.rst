This repo contains a sklearn model that is trained on house prices in California and server the prediction on a fastapi application.
The fastapi application is deployed on a local kubernetes cluster managed by minikube to serve predictions on POST request.
The application uses a redis cache to protect from repeated duplicate requests. The unit tests are using pytest and run in github actions on pusing to the repo.

If you would like to install and use poetry, please add dependancies 
using poetry and initiate application using uvicorn and test with pytest 
within the poetry shell or using poetry run commands

You can deploy the application and redis images on minikube, and test it by running using run.sh from root folder<br/>
```sh run.sh```

This run.sh scripts first trains a model an then copies the model_pipeline.pkl file<br/>
The script next starts minikube, builds the docker image mlapi<br/>
Then creates a namespace mlpredict and then deployments and services<br/>
Then starts the minikube tunnel and notes the process id<br/>
The script checks if the application is healthy<br/>
Then performs pre-defined positive and negative tests<br/>
Then kills the minikube tunnel process, delete all objects in namespace mlpredict, deletes namespace mlpredict and stops minikube.

Please note that this run script will execute without any errors if the loadbalancer gets an external-ip assigned during execution.<br/>
If the external-ip is ```<none>``` or ```pending``` during your execution, then script will wait forever for the application to be healthy.<br/> 
If you suspect the above scenario, please exit and uncomment the portforward command in the run script and execute again.
If you are not on a M1 Mac, you will need to comment the minikube tunnel command and the command that kills the process.
