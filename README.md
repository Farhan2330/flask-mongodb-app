# Deploying Flask Application and MongoDB on Minikube Kubernetes Cluster

## Overview

This guide provides step-by-step instructions to deploy a Python Flask application that interacts with a MongoDB database on a Minikube Kubernetes cluster. It also includes explanations of DNS resolution within Kubernetes and resource requests and limits for managing resources efficiently.

## Prerequisites

Ensure the following tools are installed on your system:

- Minikube
- kubectl
- Docker
- Python 3.8+
- Pip (for managing Python packages)
## **Part 1: Deploying the Flask application locally**

### **Step 1: Clone the code**

Clone the code from the repository:

```
git clone <repository_url>
```

### **Step 2:  Set Up Virtual Environment**

Create and activate a virtual environment for the Python project:

```
python3 -m venv venv
source venv/bin/activate # On Windows, use `venv\Scripts\activate`
```

### **Step 3:  Install Python Dependencies**

Install the dependencies from  `requirements.txt`:
```
pip install -r requirements.txt
```
### **Step 4:  Set Up MongoDB Using Docker**

Pull and run the MongoDB Docker image
```
docker pull mongo:latest
docker run -d -p 27017:27017 --name mongodb mongo:latest
```
This will start a MongoDB instance accessible on `localhost:27017`.
### **Step 5:   Set Up Environment Variable**

Set the `MONGODB_URI` environment variable to point to the local MongoDB instance. Create a `.env` file in the project directory with the following
```
MONGODB_URI=mongodb://localhost:27017/
MONGODB_USERNAME=
MONGODB_PASSWORD=
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
```
Load the environment variables from the `.env` file:
```
export $(cat .env | xargs)
```
### **Step 6: Run the Flask Application**
Start the Flask application:
```
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```
The Flask application should now be running on http://localhost:5000.
## Part 2:
## Step 1: Setting Up Your Environment

1. **Start Minikube**  
   Open your terminal and start Minikube:
   ```bash
   minikube start
1. **Docker Environment:**  
   Point your terminal’s Docker CLI to the Docker instance managed by Minikube:
   ```bash
   eval $(minikube docker-env)
## Step 2: Building and Pushing the Docker Image
1. **Create the Dockerfile:**  
   Create a **`Dockerfile`** in your project directory with the following content:
 ```
# Use an official Python image as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port on which the Flask app will run
EXPOSE 5000

# Set the environment variables for the Flask app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Run app.py when the container launches
CMD ["python", "app.py"]
```
2. **Build the Docker image**  
  To build the Docker image, execute the following command:
 ```
  docker build -t <image_name> .
```
3. **Test the Docker Image Locally:**  
  Run the Docker container locally to test it:
 ```
  docker run -p 5000:5000 <image_name>
  ```
## Step 3: Deploying MongoDB on Kubernetes
1. **MongoDB StatefulSet YAML:**  
Create a **`mongodb-deployment.yaml`** in your project directory with the following content:

```jsx
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
spec:
  serviceName: "mongodb"
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:latest
        ports:
        - containerPort: 27017
        volumeMounts:
        - name: mongo-persistent-storage
          mountPath: /data/db
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            secretKeyRef:
              name: flask-mongo-secrets
              key: MONGODB_USERNAME
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: flask-mongo-secrets
              key: MONGODB_PASSWORD
  volumeClaimTemplates:
  - metadata:
      name: mongo-persistent-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
```
2. **Apply the MongoDB Configuration:**  
  Deploy the MongoDB StatefulSet and Service with:
 ```
  kubectl apply -f mongodb-deployment.yaml
```
3. **create the secret directly from the command line:**  
 ```
  kubectl create secret generic mongodb-secret \
  --from-literal=mongodb-uri=' ' \
  --from-literal=mongodb-username=' ' \
  --from-literal=mongodb-password=' '

```
## Step 4:  Deploying Flask Application on Kubernetes
1. **Flask Deployment YAML:**  
Create a **`flask-deployment.yaml`** file with the following content:

```jsx
# flask-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: flask-app
  template:
    metadata:
      labels:
        app: flask-app
    spec:
      containers:
      - name: flask-app
        image: farhanahmed3/flask-mongodb-app:latest
        ports:
        - containerPort: 5000
        env:
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: flask-mongo-secrets
              key: MONGODB_URI
        - name: MONGODB_USERNAME
          valueFrom:
            secretKeyRef:
              name: flask-mongo-secrets
              key: MONGODB_USERNAME
        - name: MONGODB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: flask-mongo-secrets
              key: MONGODB_PASSWORD
        - name: FLASK_RUN_HOST
          valueFrom:
            secretKeyRef:
              name: flask-mongo-secrets
              key: FLASK_RUN_HOST
        - name: FLASK_RUN_PORT
          valueFrom:
            secretKeyRef:
              name: flask-mongo-secrets
              key: FLASK_RUN_PORT
        resources:
          requests:
            memory: "250Mi"
            cpu: "200m"
          limits:
            memory: "500Mi"
            cpu: "500m"
  ```
2. **Apply the Flask Deployment Configuration:**  
  Deploy the Flask application with:
 ```
  kubectl apply -f flask-deployment.yaml
```
## Step 4:  Service for Flask and MongoDB
1. **Service for MongoDB:**  
Create a **`mongodb-service.yaml`** file with the following content:

```jsx
apiVersion: v1
kind: Service
metadata:
  name: mongodb
spec:
  ports:
    - port: 27017
  selector:
    app: mongodb
  type: ClusterIP
```
  1. **Service for Flask:**  
Create a **`flask-service.yaml`** file with the following content:

```jsx
apiVersion: v1
kind: Service
metadata:
  name: flask-service
spec:
  type: NodePort
  selector:
    app: flask-app
  ports:
    - protocol: TCP
      port: 5000
      targetPort: 5000
      nodePort: 30001
```
2. **Apply the Services:**  
 ```
kubectl apply -f mongodb-service.yaml
kubectl apply -f flask-service.yaml
```
## Step 5: Setup Horizontal Pod Autoscaler (HPA)

1. **Create HPA for the Flask application:**  
   ```bash
   kubectl autoscale deployment flask-app --cpu-percent=70 --min=2 --max=5
   ```
## Step 6: Access the Flask Application

1. **Get the Minikube IP address:**  
   ```bash
   minikube ip
   ```
2. **Access the application via http://<minikube-ip>:30001.**  

##  DNS Resolution in Kubernetes

**DNS resolution within a Kubernetes cluster allows pods to communicate with each other using DNS names rather than IP addresses. When a Service is created, Kubernetes automatically assigns it a DNS name in the format service_name.namespace.svc.cluster.local. This DNS name can be used by other pods to access the service.**  

##  Resource Requests and Limits in K8s

**Resource requests and limits ensure that your pods have the resources they need while preventing them from consuming more than they should.**  
- Requests: The minimum amount of CPU and memory guaranteed to the pod. Kubernetes uses this to schedule the pod on a node with sufficient resources.
- Limits: The maximum amount of CPU and memory a pod can use. If the pod exceeds these limits, Kubernetes throttles or terminates the pod.

Example:
```jsx
resources:
  requests:
    memory: "250Mi"
    cpu: "0.2"
  limits:
    memory: "500Mi"
    cpu: "0.5"
```






 