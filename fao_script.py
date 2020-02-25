import pandas as pd
import pymysql


# from trade_script import trade_start

# Menu Functions
def fao_start():
    """ This brings up the first menu for the dataset."""
    ans = True
    while ans:
        ans = input("""
            Please choose where to begin searching the FAO data
            [1] FAO Codes
            [2] First FAO
            [t] Top
            """)
        if ans == "1":
            fao_codes()
        elif ans == "2":
            first_fao()
        elif ans == "t":
            # trade_start()
            pass
        else:
            print("Sorry, I didn't understand")
            fao_start()


def fao_codes():
    """ This brings up the translation menu for the dataset."""
    ans = True
    while ans:
        ans = input("""
            Which codes would you like to look up?
            [1] Countries
            [2] Products
            [t] Top
            """)
        if ans == "1":
            country_option = input(
                "Either type in a number of countries to view, or type in a keyword to search: ")
            country_view(country_option)
            fao_codes()
        elif ans == "2":
            product_option = input(
                "Either type in a number of products to view, or type in a keyword to search: ")
            product_view(product_option)
            fao_codes()
        elif ans == "t":
            fao_start()
        else:
            print("Sorry, I didn't understand.")
            fao_codes()


# Translation Functions
def country_view(country_option):
    """ Prints either a head or performs a search on the OEC country_names table. """
    df = pd.read_csv("./datasets/fao_newfoodbalance_countries.csv")
    if country_option.isdigit():
        print(df[['Country Code', 'Country']].head(int(country_option)))
    else:
        print(df[['Country Code', 'Country']][df['Country'].str.contains(country_option, case=False)])

    pass


def product_view(product_option):
    """ This extracts the product options from the OEC hs92 items. """
    df = pd.read_csv("./datasets/fao_newfoodbalance_items.csv")
    if product_option.isdigit():
        print(df[['Item Code', 'Item']].head(int(product_option)))
    else:
        print(df[['Item Code', 'Item']][df['Item'].str.contains(product_option, case=False)])

    pass


# Display Functions
def first_fao():
    """ This is not the most general FAO caller we could write but it is one of them. """
    options = input(
        "Please enter the codes for the country, product and year you would like to search for in that order with a space in between: ")
    options_list = options.split()
    df = pd.read_csv("./datasets/fao_newfoodbalance.csv", encoding='latin')
    df = df[df['Area Code'] == int(options_list[0])]
    df = df[df['Item Code'] == int(options_list[1])]
    df = df[df['Year Code'] == int(options_list[2])]
    print(df)

    pass
