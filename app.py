import streamlit as st
import numpy as np
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



st.header('Product Recommender System')
st.sidebar.header("Navigation")
st.sidebar.subheader("Select your product preference")
st.sidebar.text_input('Number of recommendations')


search_term = st.text_input('Search for a product:')
def search_products(search_term):
    if search_term:
        # Filter the products based on the search term
        results = updated_products[updated_products['Name'].str.contains(search_term, case=False, na=False)]
        return results
    return updated_products  # Return all products if no search term

# Get search results
search_results = search_products(search_term)


# Display search results
if not search_results.empty:
    selected_product = st.sidebar.selectbox('Select a product:', search_results['Name'])
else:
    st.write("No products found.")


# Filter by category
selected_category = st.sidebar.selectbox('Select a category:', options=['All', 'Nail Care', 'Hair Care', 'Skin Care'])
# Attempt to access the KNN model based on the structure of model_data

if isinstance(model_data, dict):
    # Display the contents of model_data to understand its structure
    st.write("Detailed model_data content:", model_data)
else:
    model = model_data  # Directly use if model_data is already the model

# Assuming your model is either the direct object or you need to find it in the dictionary:
if isinstance(model_data, dict):

    model_key = None  # Set this to the key that holds your model
    for key in model_data.keys():
        st.write(f"Key: {key}, Type: {type(model_data[key])}")  
        if 'knn' in key.lower():  
            model_key = key
            break
    
    if model_key:
        model = model_data[model_key]
        st.write(f"Using model from key: {model_key}")
    else:
        st.error("KNN model key not found in model_data.")
else:
    model = model_data  # Directly use if model_data is already the model



#to display the trending items
trending_products = updated_products.head(10)  
def display_trending_products():
    st.subheader("Top Trending Products")
    cols = st.columns(5)  # Create 5 columns for layout
    for i, row in trending_products.iterrows():
        with cols[i % 5]:  # Cycle through columns
            st.markdown(f'''
                <div class="product-container">
                    <img src="{row["ImageURL"]}" class="product-image" width="120">
                    <div class="product-genres"></div>
                </div>
            ''', unsafe_allow_html=True)
            st.text(row['Name'])

            if st.button(f'Buy ', key=f'buy_trending_{i}'):
                st.success(f"You have selected to buy {row['Name']}!")


display_trending_products()    
def get_collaborative_based_recommendations(selected_product, top_n):
    product_id = updated_products[ updated_products['Name'] == selected_product].index[0]
    distance, suggestion = model_data.kneighbors(user_item_matrix.iloc[product_id,:].values.reshape(1,-1), n_neighbors= top_n )
    col_recommended_products = user_item_matrix.index[suggestion[0]]  
    return col_recommended_products

def get_content_based_recommendations(Name, top_n):
    index = updated_products[ updated_products['Name'] == Name].index[0]
    similarity_scores =  cosine_similarities_content[index]
    similar_indices = similarity_scores.argsort()[::-1][1:top_n + 1]
    content_recommended_products= updated_products.loc[similar_indices, 'Name'].values
    return content_recommended_products

def hybrid_recommendations(selected_product, top_n):
    col_recommended_products = get_collaborative_based_recommendations(selected_product, top_n)
    content_recommended_products = get_content_based_recommendations(selected_product, top_n)

    # Ensure that col_recommended_products contains only strings
    col_recommended_products = [str(Name).replace("'", "") for Name in col_recommended_products if isinstance(Name, str)]
    content_recommended_products = [str(Name).replace("'", "") for Name in content_recommended_products if isinstance(Name, str)]
    
    products_name = list(set(col_recommended_products) | set(content_recommended_products))
    products_name = products_name[:top_n]
    
    products = updated_products[updated_products['Name'].isin(products_name)]
    product_names = products['Name'].tolist()
    product_urls = products['ImageURL'].tolist()  # Assuming the column for images
    product_genres = products['Category'].tolist()  # Assuming the column for categories
    product_ratings = products['Rating'].tolist()


    return product_names, product_urls, product_genres, product_ratings
if st.button('Show Recommendation'):
    recommended_products, product_url, product_genres, product_rating = hybrid_recommendations(selected_product, 6)
    cols = st.columns(5)

    for i in range(1, 6):
        with cols[i-1]:
            
            st.markdown(f'<div class="product-container"><img src="{product_url[i]}" class="product-image" width="120"><div class="product-genres"></div></div>', unsafe_allow_html=True)
         
            st.text(recommended_products[i])


            if st.button(f'Buy', key=f'buy_{i}'):
                st.success(f"You have selected to buy {recommended_products[i]}!")

if st.button('Show Seasonal Items'):
    # Assuming the 'Tags' or 'Category' column contains seasonal items
    seasonal_items = updated_products[updated_products['Tags'].str.contains('seasonal', case=False, na=False)]

    if not seasonal_items.empty:
        cols = st.columns(5)  
        for i, row in seasonal_items.iterrows():
            if i >= 5:  
                break
            with cols[i]:
             
                st.markdown(f'<div class="product-container"><img src="{row["ImageURL"]}" class="product-image" width="120"><div class="product-genres"></div></div>', unsafe_allow_html=True)
                st.text(row['Name']) 
    else:
        st.write("No seasonal items found.")

# Add custom CSS
st.markdown(
    """
    <style>
    .prodcut-container {
        height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .product-image {
        flex-grow: 1;
    }
    .product-genres {
        margin-top: 10px;
        text-align: center;
        
    }
    .buy-button {
        background-color: #4CAF50; /* Green background */
        color: white; /* White text */
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px; /* Rounded corners */
    }
    .buy-button:hover {
        background-color: #45a049; /* Darker green on hover */}


    .seasonal-button{
        margin-left:'12px'
    }
   .product {
    width: 300px;            /* Set the width of the product container */
    height: 300px;           /* Set the height of the product container */
    background-image: url('https://th.bing.com/th/id/OIP.EWEYdFJYUk1PZA3KGkrg2wHaHa?rs=1&pid=ImgDetMain');

    background-size: cover;  /* Ensure the image covers the entire container */
    background-position: center; /* Center the image */
    border: 1px solid #ccc;  /* Optional: add a border for visual separation */
    display: flex;           /* Flexbox to center content, if any */
    justify-content: center; /* Center horizontally */
    align-items: center;     /* Center vertically */
    color: #fff;             /* Text color, if you want to add labels */
    text-align: center;      /* Center text */
}

.placeholder-label {
    display: none; /* Initially hide label */
}

.product:hover .placeholder-label {
    display: block; /* Show label on hover, if desired */
}


    </style>
    """, unsafe_allow_html=True
)

print("Done")


