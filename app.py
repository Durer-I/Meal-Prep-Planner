import streamlit as st
import pandas as pd
import numpy as np
import sqlite3 as db

st.set_page_config(page_title= "Meal Prep Planner", layout="wide", page_icon="🍜")


###DATABASE INITIALIZATION####
conn_ingredient = db.connect(f"DataBase/ingredient.db")
conn_recipe = db.connect(f"DataBase/recipe.db")
conn_notes = db.connect(f"DataBase/notes.db")
conn_tags = db.connect(f"DataBase/tags.db")
conn_macros = db.connect(f"DataBase/macros.db")



def MealFinder(mealtype, cal):

    recipes = {}
    macrosTotal = [0,0,0,0]
    
    for i in range(len(mealtype)):
        nm =len(mealType)
        cpm = cal/nm
        k = 0
        buffer = pd.read_sql(f"SELECT * FROM {mealtype[i]}", con=conn_tags)
        li = []
        for j in range(len(buffer)): 
            bufferMacros = pd.read_sql(f"SELECT * FROM {buffer.loc[j,'Name']}", con=conn_macros)
            li.append(bufferMacros.loc[0,"Calories"])
        array = np.asarray(li)
        idx = (np.abs(array - cpm)).argmin()
        recipes[mealType[i]] = buffer.loc[idx,"Name"]

        nm-=1

        buffer = pd.read_sql(f"SELECT * FROM {buffer.loc[idx,'Name']}", con=conn_macros)
        cal-=buffer.loc[0,"Calories"]
        for i in buffer.columns:
            macrosTotal[k] += buffer.loc[0,i]
            k+=1
    
    return recipes, macrosTotal





##Sidebar##
with st.sidebar:
    # with st.form("Title",border=False,clear_on_submit=False):
    
    err = False

    meals = st.slider("Number of meal prep days", label_visibility="visible",
            min_value=1, max_value=6, step=1, )

    # dietType = st.radio ("Choose your preffered diet:",
    #                     ["Vegetarian","Vegan","Omnivorous"], 
    #                     help= "Select your dieteary restrictions", 
    #                     horizontal=True)
    
    calories = st.number_input(" Please enter Your calorie intake:", 
                            min_value= 0, max_value= 4000,step= 1
                                )
    while calories == 0: 
        err = st.error("Calories cannot be zero") 
        break
    
    col1, col2, col3 = st.columns(3, gap="small")
    with col1: macroProtein = (st.number_input("Protein%", min_value=0,max_value=100, step=1))
    with col2: macroCarb = st.number_input("Carb%", min_value=0,max_value=100, step=1)
    with col3: macroFat = st.number_input("Fats%", min_value=0,max_value=100, step=1)
    while macroCarb+macroFat+macroProtein != 100: 
        err = st.error("Macro total should be 100%") 
        break
    
    split = {"Protein": macroProtein,"Carb": macroCarb,"Fat": macroFat}
    
    # days = st.number_input(" Please enter the number of meal prep days:", 
    #                         min_value= 0, max_value= 5,step= 1, value=1
    #                             )
    
    mealType = st.multiselect("What meals would you like to include?", options= ["Breakfast", "Lunch", "Dinner", "Snacks"])
    while mealType == []: 
        err = st.error("Meals need to be selected") 
        break

    # groceryList = st.radio("Would you like a grocery list:", options= ["Yes", "No"], horizontal=True)

    dis = False
    if err: dis = True
    submit = st.button("Get Plan!!", type="primary", use_container_width=True, disabled= dis)

    # submit = st.form_submit_button("Get Plan!!", type="primary",use_container_width=True)





if submit == True:

    name,total = MealFinder(mealtype=mealType, cal = calories)

    st.header(f"Macro Comparison:")
    
    col = st.columns(3, gap="small")
    with col[0]: 
        st.subheader("Input")
        st.write(f"Calories: {calories}  \nProtein: {round(((macroProtein/100)*calories)/4)}g  \nCarbs: {round(((macroCarb/100)*calories)/4)}g  \nFats: {round(((macroFat/100)*calories)/9)}g")

    with col[2]:
        st.subheader("Meal Plan")
        st.write(f"Calories: {total[0]}  \nProtein: {total[2]}g  \nCarbs: {total[1]}g  \nFats: {total[3]}g" )
    
    
    
    for i in range(len(mealType)):

        with st.expander(mealType[i]):

            ingredient = pd.read_sql(f"SELECT * FROM {name[mealType[i]]}", con=conn_ingredient)
            recipe = pd.read_sql(f"SELECT * FROM {name[mealType[i]]}", con=conn_recipe)
            notes = pd.read_sql(f"SELECT * FROM {name[mealType[i]]}", con=conn_notes)
            macros = pd.read_sql(f"SELECT * FROM {name[mealType[i]]}", con=conn_macros)

            st.header(name[mealType[i]])

            st.subheader("Ingredients")

            for i in range(len(ingredient)):
                st.write(f"{(ingredient.loc[i,'Quantity'])*meals}  {ingredient.loc[i,'Unit']}  {ingredient.loc[i,'Type']}")
            
            st.subheader("Recipe")
            for i in range(len(recipe)): st.write(f"{(recipe.loc[i,'Recipe'])}")

            st.subheader("Notes")
            for i in range(len(notes)-1): st.write(f"{(notes.loc[i,'Notes'])}")

            st.subheader("Macros")
            for i in range(len(macros)):  st.write(f"Calories: {macros.loc[i,'Calories']}  \nCarbs: {macros.loc[i,'Carbs']}  \nProtein:{macros.loc[i,'Protein']}  \nFats: {macros.loc[i,'Fats']}")

            st.write(f"***Receipe Source***: {notes.iloc[-1].values[0]}")
        



###HOME PAGE###
else: 
    st.title("Welcome!!!")

    st.header("*Meal Prep Planner* – your personal meal prep companion!")

    st.write("We know life can be hectic, but eating well shouldn’t be. Whether you’re chasing fitness goals or simply aiming for balanced, wholesome meals, we’re here to make it easier. **Meal Prep Planner** crafts personalized meal plans tailored to your unique needs – from calories to macros and even how many meals fit into your day.")

    st.subheader("How It Works:")

    st.info("**1. Tell Us About You:** Set your daily calorie goal, and let us know your preferred protein, carb, and fat ratios.  \n\
	           **2.  Choose Your Schedule:** Want three square meals or six smaller bites? You decide!  \n\
	           **3. Get Your Plan:** Receive a curated meal plan with easy-to-follow recipes, designed for your life.")

    st.write("We’re not just another meal prep tool; we’re your partner in creating a balanced lifestyle that fuels your body and mind. Whether you’re new to meal planning or a seasoned pro, **Meal Prep Planner** grows with you – one meal at a time.")

    st.success("\nTake control of your nutrition with us. It’s time to simplify meal prep, and enjoy what you eat. Let’s get started!")
    
    st.write("***NOTE:***  \n\
             1. New meals are constatntly being added!!  \n\
             2. We are aware of an error with not optimizing macros. We are working hard to resolve it. We appreciate your patience!!")
    st.write("***Version: v0.1***")
    
    # st.balloons()




conn_ingredient.close()
conn_recipe.close()
conn_notes.close()
conn_tags.close()
conn_macros.close()