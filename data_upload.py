import pickle
import streamlit as st
import numpy as np

#model_data = pickle.load(open('artifacts/collaborative_filtering_model.pkl','rb'))
model_data = pickle.load(open('artifacts/knn_model.pkl', 'rb'))

user_item_matrix = pickle.load(open('artifacts/user_item_matrix.pkl','rb'))
updated_products = pickle.load(open('artifacts/updated_products.pkl','rb'))
cosine_similarities_content= pickle.load(open('artifacts/cosine_similarities_content.pkl','rb'))
filtered_products = updated_products['Name'].unique() 

print("Begin")