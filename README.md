# Dependencies Game API

## Description

This API manages the health status of several entities with dependencies. Each entity has a boolean health status. The primary entity is robots, which require alimentation, guidance, and an active license.

## Installation

1. Clone the repository:
    ```bash
    git clone <REPOSITORY_URL>
    cd Dependencies_game
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1. Start the FastAPI application:
    ```bash
    uvicorn src.main:app --reload
    ```

2. Access the interactive API documentation:
    Open your browser and go to `http://127.0.0.1:8000/docs`

## Project Structure

```
Dependencies_game/
│
├── src/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── crud.py
│   └── routers/
│       ├── robots.py
│       ├── alimentations.py
│       ├── guidages.py
│       └── licences.py
│
├── requirements.txt
├── README.md
└── logging_config.py
```

## Endpoints

### Robots
- `POST /robots/` : Create a new robot
- `GET /robots/{robot_id}` : Get a robot by ID
- `GET /robots/` : Get a list of robots with optional filters
- `PUT /robots/{robot_id}/status` : Update the health status of a robot
- `PUT /robots/update_health_status` : Update the health status of all robots based on related objects

### Alimentations
- `POST /alimentations/` : Create a new alimentation
- `GET /alimentations/{alimentation_id}` : Get an alimentation by ID
- `GET /alimentations/` : Get a list of alimentations
- `PUT /alimentations/{alimentation_id}/status` : Update the health status of an alimentation

### Guidages
- `POST /guidages/` : Create a new guidance system
- `GET /guidages/{guidage_id}` : Get a guidance system by ID
- `GET /guidages/` : Get a list of guidance systems
- `PUT /guidages/{guidage_id}/status` : Update the health status of a guidance system

### Licences
- `POST /licences/` : Create a new license
- `GET /licences/{licence_id}` : Get a license by ID
- `GET /licences/` : Get a list of licenses
- `PUT /licences/{licence_id}/status` : Update the health status of a license

## Dependencies and Health Status Behavior

### Robots
- Robots depend on alimentation, guidance, and license.
- A robot's `isHealthy` status is `True` if all related objects (alimentation, guidance, and license) are `isHealthy == True`.
- If any related object is `isHealthy == False`, the robot's `isHealthy` status will be updated to `False`.

### Alimentations
- Alimentations have a type (`SOLAIRE` or `NUCLEAIRE`) and a health status (`isHealthy`).
- The health status of alimentations can be updated, and if set to `False`, it will trigger an update to the health status of related robots.

### Guidages
- Guidages have a health status (`isHealthy`).
- The health status of guidages can be updated, and if set to `False`, it will trigger an update to the health status of related robots.

### Licences
- Licences have an expiration date and a health status (`isHealthy`).
- The health status of licenses is automatically checked based on the expiration date.
- The health status of licenses can be updated, and if set to `False`, it will trigger an update to the health status of related robots.

## Gestion de l'énergie

L'API inclut désormais des fonctionnalités de gestion de l'énergie pour surveiller et contrôler la consommation d'énergie des robots et la capacité des alimentations.

### Consommation d'énergie des robots

Chaque robot consomme de l'énergie en fonction de son type de moteur :
- **PETIT** : 10 unités
- **MOYEN** : 20 unités
- **GRAND** : 30 unités

Cette consommation est calculée via la propriété `power_consumption` sur le modèle Robot.

### Capacité de l'alimentation et gestion de la charge

Chaque alimentation (`Alimentation`) a une `capacité` qui définit la puissance maximale qu'elle peut fournir. Le système vérifie périodiquement si la puissance totale consommée par tous les robots sains connectés à une alimentation dépasse sa capacité.

Si une alimentation est surchargée, le système éteint automatiquement les robots pour réduire la charge. Les robots sont désactivés dans l'ordre de priorité suivant :
1. Les robots ayant la plus grande consommation d'énergie sont éteints en premier.
2. En cas d'égalité de consommation d'énergie, le robot avec l'ID le plus élevé est éteint en premier.

Cette logique est gérée par la fonction `update_power_health_status`, qui est appelée dans `update_robots_health_status`.

## License

This project is licensed under the MIT License.