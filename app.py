from flask import Flask, render_template, request
from supabase import create_client, Client
import os
import pandas as pd
import ast

# Initialize Supabase client
url = "https://pfzxkjlmismuwjpcvtzl.supabase.co"  # Your Supabase project URL
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBmenhramxtaXNtdXdqcGN2dHpsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzU2NzE3ODEsImV4cCI6MjA1MTI0Nzc4MX0.RGriaqNP86UAjSkzE-zGc0koIga8TtJRgPngz8QYB00"  # Your Supabase anon key
supabase: Client = create_client(url, key)

# Fetch data from Supabase
try:
    response = supabase.table('recipes').select('*').execute()
    data = pd.DataFrame(response.data)
    print("Dataset loaded successfully.")
    
    # Drop the first 'Number' column if it exists
    if 'Number' in data.columns:
        data = data.drop(columns=['Number'])
    
    # Check if the required columns exist
    print("Columns in the dataset:", data.columns)
    print(data.head())
    
    # Convert string representations of lists into actual lists
    if 'Ingredients' in data.columns and 'Cleaned_Ingredients' in data.columns:
        data['Ingredients'] = data['Ingredients'].apply(ast.literal_eval)
        data['Cleaned_Ingredients'] = data['Cleaned_Ingredients'].apply(ast.literal_eval)
    else:
        print("Error: Required columns not found in the dataset")
        data = pd.DataFrame()

except Exception as e:
    print("Error loading dataset:", e)
    data = pd.DataFrame()

# Initialize Flask app
app = Flask(__name__, static_folder='static')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # Get input ingredients from the form
    input_ingredients = request.form.get('ingredients')
    print("Received input ingredients:", input_ingredients)

    if not input_ingredients:
        return render_template('results.html', recipes=[], message="No ingredients provided.")

    # Process input ingredients into a list of lowercased, stripped terms
    input_ingredients_list = [ingredient.strip().lower() for ingredient in input_ingredients.split(",")]
    print("Input ingredients list:", input_ingredients_list)

    # Filter recipes based on matching any part of the ingredients
    def ingredient_match(cleaned_ingredients):
        # Check if any of the input ingredients are a substring of the recipe ingredients
        for input_ingredient in input_ingredients_list:
            for ingredient in cleaned_ingredients:
                if input_ingredient in ingredient.lower():
                    return True
        return False

    # Apply the matching function
    if not data.empty and 'Cleaned_Ingredients' in data.columns:
        filtered_data = data[data['Cleaned_Ingredients'].apply(ingredient_match)]

        # Convert filtered recipes to a list of dictionaries for rendering
        recipes = filtered_data[['Title', 'Ingredients', 'Instructions', 'Image_Name']].to_dict(orient='records')

        if recipes:
            return render_template('results.html', recipes=recipes, message=f"Found {len(recipes)} recipes.")
        else:
            return render_template('results.html', recipes=[], message="No recipes found with those ingredients.")
    else:
        return render_template('results.html', recipes=[], message="Dataset is empty or required columns not found.")

@app.route('/search_by_title', methods=['POST'])
def search_by_title():
    # Get input title from the form
    input_title = request.form.get('title')
    print("Received input title:", input_title)

    if not input_title:
        return render_template('results.html', recipes=[], message="No title provided.")

    # Filter recipes based on matching the title
    if not data.empty and 'Title' in data.columns:
        filtered_data = data[data['Title'].str.contains(input_title, case=False, na=False)]

        # Convert filtered recipes to a list of dictionaries for rendering
        recipes = filtered_data[['Title', 'Ingredients', 'Instructions', 'Image_Name']].to_dict(orient='records')

        if recipes:
            return render_template('results.html', recipes=recipes, message=f"Found {len(recipes)} recipes with title matching '{input_title}'.")
        else:
            return render_template('results.html', recipes=[], message="No recipes found with that title.")
    else:
        return render_template('results.html', recipes=[], message="Dataset is empty or required columns not found.")

if __name__ == '__main__':
    app.run()
    #debug=True
