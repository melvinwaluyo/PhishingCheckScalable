# Phishing Check - Scalable Microservices Architecture

This repository contains the **scalable, microservices-based version** of the Phishing Check application. It's designed for deployment on Kubernetes and addresses the limitations of the original monolithic design by separating concerns, enabling independent scaling, and improving resilience.

## 1. Architecture Overview

The system is designed to receive text input, predict whether it's a phishing attempt using a machine learning model, and store the results, incorporating caching for performance. It leverages Kubernetes for orchestration, Nginx for ingress, PostgreSQL for data storage, and Redis for caching.

![Scalable Architecture Diagram](/ScalableArchitecture.drawio.png)

## 2. Core Components & Technologies

The application is broken down into several key components:

- **Backend Service (`backend`)**:
  - **Technology:** Python, FastAPI, SQLAlchemy
  - **Purpose:** Handles incoming API requests, orchestrates the prediction process, interacts with the cache (Redis) and the database (PostgreSQL), and communicates with the ML Model Service.
  - **Code:** `main.py`, `app/routes/predict.py`, `app/db.py`, etc.
- **ML Model Service (`MLservice`)**:
  - **Technology:** Python, FastAPI, Scikit-learn (Joblib)
  - **Purpose:** A dedicated microservice responsible for loading the trained SVM model and vectorizer, receiving text from the Backend Service, and returning prediction results and probabilities.
  - **Code:** `ml_main.py`
- **PostgreSQL Database (`db`)**:
  - **Technology:** PostgreSQL (Containerized)
  - **Purpose:** Persistently stores the results of each phishing prediction, including the input text, verdict, and accuracy.
- **Redis Cache (`redis`)**:
  - **Technology:** Redis (Containerized)
  - **Purpose:** Caches prediction results based on input text to reduce redundant calls to the ML Model Service and speed up responses for repeated queries.
- **Nginx Ingress Controller**:
  - **Technology:** Nginx (via Kubernetes Ingress)
  - **Purpose:** Acts as the single entry point for all external traffic. It routes requests based on paths (e.g., `/api/predict`) to the appropriate internal Kubernetes service (primarily the Backend Service).

## 3. Kubernetes Deployment

The application is deployed and managed using Kubernetes, leveraging several key resources:

- **Docker Images:** Both `backend` and `MLservice` are packaged into Docker images using hardened `Dockerfile`s (non-root users, updated packages).
- **Deployments:** Manage the stateless `backend` and `MLservice` pods, handling replicas and updates.
- **StatefulSets:** Manage the stateful `postgres` and `redis` pods, ensuring stable storage and network identifiers.
- **Services (`ClusterIP`)**: Provide stable internal DNS names and load balancing (`postgres-svc`, `redis-svc`, `mlservice-svc`, `backend-svc`) for communication _within_ the cluster.
- **PersistentVolumeClaims (PVCs):** Request and manage persistent storage for PostgreSQL and Redis, ensuring data survives pod restarts.
- **Secrets:** Securely manage sensitive data like the PostgreSQL password.
- **ConfigMaps:** Manage non-sensitive configuration data like database hostnames, Redis details, and service URLs.
- **Ingress:** Defines rules for the Nginx Ingress Controller to route external HTTP traffic to internal services.
- **HorizontalPodAutoscaler (HPA):** Automatically scales the number of `backend` pods based on CPU utilization to handle varying loads.

## 4. Request Flow

A typical prediction request follows these steps:

1.  A client sends a `POST` request to `http://<your-host>/api/predict`.
2.  The request hits the Nginx Ingress Controller.
3.  Ingress routes the request to the `backend-svc`.
4.  The `backend-svc` load balances the request to an available `backend` pod.
5.  The `backend` pod checks Redis (`redis-svc`) for a cached result.
6.  **Cache Hit:** If found, the cached result is retrieved, and a response is sent back (skipping steps 7-9).
7.  **Cache Miss:** If not found, the `backend` pod sends a request to the `mlservice-svc`.
8.  The `mlservice-svc` routes the request to an `mlservice` pod, which performs the prediction and returns the result.
9.  The `backend` pod receives the result, stores it in Redis, and stores it in PostgreSQL (`postgres-svc`).
10. The `backend` pod sends the final response back through the Ingress to the client.

## 5. Local Development & Deployment

- **Setup:** The system can be run locally using Docker Desktop with Kubernetes enabled.
- **Deployment:** All Kubernetes resources are defined in YAML files within the `kubernetes/` directory and applied using `kubectl apply -f kubernetes/`.
- **Access:** The API is accessed via `http://localhost/api/predict` (through Nginx Ingress), and PostgreSQL can be accessed using `kubectl port-forward` and pgAdmin.
