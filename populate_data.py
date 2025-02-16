import requests
import random
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def create_licence():
    expiration_date = datetime.utcnow() + timedelta(days=random.randint(30, 365))
    licence_data = {
        "isHealthy": True,
        "expiration_date": expiration_date.isoformat()
    }
    response = requests.post(f"{BASE_URL}/licences/", json=licence_data)
    response.raise_for_status()
    return response.json()

def create_guidage():
    guidage_data = {
        "isHealthy": True
    }
    response = requests.post(f"{BASE_URL}/guidages/", json=guidage_data)
    response.raise_for_status()
    return response.json()

def create_alimentation(type):
    alimentation_data = {
        "alimentationType": type,
        "isHealthy": True
    }
    response = requests.post(f"{BASE_URL}/alimentations/", json=alimentation_data)
    response.raise_for_status()
    return response.json()

def create_robot(name, alimentation_id, guidage_id, licence_id):
    robot_data = {
        "name": name,
        "isHealthy": True,
        "alimentation_id": alimentation_id,
        "guidage_id": guidage_id,
        "licence_id": licence_id,
    }
    response = requests.post(f"{BASE_URL}/robots/", json=robot_data)
    response.raise_for_status()
    return response.json()

def main():
    # Create licences
    print("Creating licences...")
    licences = [create_licence() for _ in range(10)]
    print(f"Created {len(licences)} licences.")

    # Create guidages
    print("Creating guidages...")
    guidages = [create_guidage() for _ in range(3)]
    print(f"Created {len(guidages)} guidages.")

    # Create alimentations
    print("Creating alimentations...")
    alimentations = []
    for _ in range(50):
        alimentations.append(create_alimentation("SOLAIRE"))
        alimentations.append(create_alimentation("NUCLEAIRE"))
    print(f"Created {len(alimentations)} alimentations.")

    # Create robots
    print("Creating robots...")
    for i in range(100):
        name = f"Robot_{i+1}"
        alimentation = random.choice(alimentations)
        guidage = guidages[i % len(guidages)]
        licence = licences[i % len(licences)]
        create_robot(name, alimentation["id"], guidage["id"], licence["id"])
    print("Created 100 robots.")

if __name__ == "__main__":
    main()
