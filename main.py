from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import os

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Recipe model
class Recipe(BaseModel):
    id: int
    title: str
    cuisine: str
    rating: float
    total_time: int
    serves: int
    description: str

# Load recipes from JSON file
DATA_FILE = os.path.join(os.path.dirname(__file__), "sample_recipes.json")

def load_recipes() -> List[Recipe]:
    with open(DATA_FILE, "r") as f:
        return [Recipe(**r) for r in json.load(f)]

def save_recipes(recipes: List[Recipe]):
    with open(DATA_FILE, "w") as f:
        json.dump([r.dict() for r in recipes], f, indent=2)

recipes: List[Recipe] = load_recipes()

# --- APIs ---
@app.get("/recipes", response_model=List[Recipe])
def get_recipes():
    return recipes

@app.get("/recipes/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int):
    recipe = next((r for r in recipes if r.id == recipe_id), None)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@app.post("/recipes", response_model=Recipe)
def add_recipe(recipe: Recipe):
    if any(r.id == recipe.id for r in recipes):
        raise HTTPException(status_code=400, detail="Recipe with this ID already exists")
    recipes.append(recipe)
    save_recipes(recipes)
    return recipe

@app.put("/recipes/{recipe_id}", response_model=Recipe)
def update_recipe(recipe_id: int, updated: Recipe):
    for idx, r in enumerate(recipes):
        if r.id == recipe_id:
            recipes[idx] = updated
            save_recipes(recipes)
            return updated
    raise HTTPException(status_code=404, detail="Recipe not found")

@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
    global recipes
    recipes = [r for r in recipes if r.id != recipe_id]
    save_recipes(recipes)
    return {"message": "Recipe deleted successfully"}
