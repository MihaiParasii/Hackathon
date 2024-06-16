from typing import List

class UserPreferences:
    def __init__(self, id:str, categories: List[str], brands: List[str], models: List[str]):
        self.id = id
        self.categories = categories
        self.brands = brands
        self.models = models

    def __init__(self, id:str):
        self.id = id
        self.categories = []
        self.brands = []
        self.models = []

    def __str__(self):
        return f"UserPreferences(categories={self.categories}, brands={self.brands}, models={self.models})"