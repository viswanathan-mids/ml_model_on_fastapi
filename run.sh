#!/bin/bash

#Run this script from root directory

IMAGE_NAME=mlapi

echo -e "Training the model, please wait.....\n"
#python $PWD/trainer/train.py
#mv $PWD/model_pipeline.pkl $PWD/mlapi/

echo -e "\nModel is trained."

# start minikube
minikube start --kubernetes-version=v1.22.6

# set docker to point to minikube 
eval $(minikube -p minikube docker-env)

# push image to minikube docker
echo -e "\nBuilding a new docker image"
docker build -t ${IMAGE_NAME} -f "$PWD/mlapi/Dockerfile" $PWD/mlapi/

# yaml files are sequenced inside infra such that namespace is applied first
# and then deployments and services
kubectl apply -f "$PWD/mlapi/infra"

# If you are not on M1 Mac, comment the below two steps
# start the minikube tunnel and store the process id
#minikube tunnel &
#MINIKUBE_PID=`ps -ef | awk '/minikube tunnel/{ print $2 }' | head -n 1`

sleep 6

# wait for app deployment to be successfully rolled out
echo -e "\nWaiting for app deployment to be successfully rolled out.. please wait"

# Checking for atleast 1 available pod before proceeding to the next steps.
# This check is also mandatory in case of using port-forward command, as it will error out if the pod is not ready 

available=0
while [ $available -eq 0 ]
do
    deploys=$(kubectl get deployment predictapi-deployment -n mlpredict | tail -n +2 | awk '{print $4}')
    if [ $deploys -gt 0 ]; then
        available=1
        echo -e "\n"predictapi-deployment" successfully rolled out\n"
    fi
    sleep 5 #wait before retrying
done

# Uncomment the below port-forward command only if the predictapi-service loadbalancer 
# has external-ip as 'pending' or <none> during your execution 

kubectl port-forward -n mlpredict service/predictapi-service 8000:8000 &
sleep 3

echo -e "\nChecking if the application is healthy before proceeding"

# checking application health and proceeding only when we get a successful response
status=0
while [ $status -eq 0 ]
do
    result=$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://127.0.0.1:8000/health")
    if [ $result -eq "200" ]; then
        status=1
        echo -e "\nApplication is healthy"
    else echo -e "\nApplication is not responding..please wait"
    fi
    sleep 5 #wait before retrying
done


# Application tests
echo -e "\nBasic tests"
echo -e "\nPositive test. Accessing url 'http://127.0.0.1:8000/hello?name=vish'"
curl -s -w "\nStatus code: %{http_code}\n" 'http://127.0.0.1:8000/hello?name=vish'

echo -e "\nNegative test. Accessing url 'http://127.0.0.1:8000/hello?ne=vish'"
curl -s -w "\nStatus code: %{http_code}\n" 'http://127.0.0.1:8000/hello?ne=vish'

echo -e "\nPositive test. Accessing url 'http://127.0.0.1:8000/openapi.json'"
curl -s -w "\nStatus code: %{http_code}\n" 'http://127.0.0.1:8000/openapi.json'

echo -e "\nNegative test acessing http://127.0.0.1:8000/"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://127.0.0.1:8000/"

echo -e "\nPositive test accessing http://127.0.0.1:8000/docs"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://127.0.0.1:8000/docs"

echo -e "\nTests for /predict endpoint"
echo -e "\nPositive test. Single sample"
curl -s -w "\nStatus code: %{http_code}\n" -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d \
'{"samples":[{"HouseAge":"41","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02","Population":"322","AveOccup":"2.55","Latitude":"37.88","Longitude":"-122.21"}]}'

echo -e "\nPositive test. Three samples"
curl -s -w "\nStatus code: %{http_code}\n" -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d \
'{"samples":[{"AveRooms":"6.98","AveBedrms":"1.02","Population":"321","AveOccup":"2.55","Latitude":"37.88","Longitude":"-122.21","HouseAge":"41","MedInc":"8.32"},
{"AveRooms":"6.98","AveBedrms":"1.02","Population":"322","AveOccup":"2.55","Latitude":"37.88","Longitude":"-122.21","HouseAge":"4","MedInc":"8.24"},
{"AveRooms":"6.98","AveBedrms":"1.02","Population":"322","AveOccup":"2.55","Latitude":"37.88","Longitude":"-122.21","HouseAge":"2","MedInc":"8.24"}]}'

echo -e "\nPositive test. One additional feature with all required features"
curl -s -w "\nStatus code: %{http_code}\n" -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d \
'{"samples":[{"HouseAge":"41","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02","Population":"322","AveOccup":"2.55","Latitude":"37.88","Longitude":"-122.21","Zone":"1"}]}'

echo -e "\nPositive test. All required features in different order"
curl -s -w "\nStatus code: %{http_code}\n" -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d \
'{"samples":[{"AveRooms":"6.98","AveBedrms":"1.02","Population":"322","AveOccup":"2.55","Latitude":"37.88","Longitude":"-122.21","HouseAge":"41","MedInc":"8.32"}]}'

echo -e "\nNegative test. A required feature is not the correct type"
curl -s -w "\nStatus code: %{http_code}\n" -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d \
'{"samples":[{"HouseAge":"41","MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02","Population":"322K","AveOccup":"2.55","Latitude":"37.88","Longitude":"-122.21"}]}'

echo -e "\nNegative test. A required feature missing in the request"
curl -s -w "\nStatus code: %{http_code}\n" -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d \
'{"samples":[{"MedInc":"8.32","AveRooms":"6.98","AveBedrms":"1.02","Population":"322","AveOccup":"2.55","Latitude":"37.88","Longitude":"-122.21"}]}'

echo -e "\nNegative test. Empty request"
curl -s -w "\nStatus code: %{http_code}\n" -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d '{}'

echo -e "\nTests complete. Cleanup starting..\n"

Sleep 5

# killing minikube tunnel process
#kill -9 $MINIKUBE_PID

# deleting all objects and namespace
kubectl delete all --all -n mlpredict
kubectl delete namespace mlpredict

# stopping minikube
minikube stop
