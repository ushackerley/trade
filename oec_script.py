import oec
import json
import pandas as pd
from engineering_notation import EngNumber
import pymysql


# from trade_script import trade_start

# Menus
def oec_start():
    """ This brings up the first menu for the dataset."""
    ans = True
    while ans:
        ans = input("""
            Please choose where to begin searching the OEC.
			[1] OEC Codes
			[2] First OEC
			[t] Top
			""")
        if ans == "1":
            oec_codes()
        elif ans == "2":
            first_oec()
        elif ans == "t":
            # trade_start()
            pass
        else:
            print("Sorry, I didn't understand")
            oec_start()


def oec_codes():
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
            oec_codes()
        elif ans == "2":
            product_option = input(
                "Either type in a number of products to view, or type in a keyword to search: ")
            product_view(product_option)
            oec_codes()
        elif ans == "t":
            oec_start()
        else:
            print("Sorry, I didn't understand.")
            oec_codes()


# Translation Functions
def country_view(country_option):
    """ Prints either a head or performs a search on the OEC country_names table. """
    df = pd.read_csv("./datasets/oec_country_names.tsv", delim_whitespace=True)
    if country_option.isdigit():
        print(df.head(int(country_option)))
    else:
        print(df[df['name'].str.contains(country_option, case=False)])

    pass


def product_view(product_option):
    """ This extracts the product options from the OEC hs92 items. """
    df = pd.read_csv("./datasets/oec_products_hs_92.tsv", delim_whitespace=True)
    df = df[df['id'].apply(lambda x: len(x) == 6)]
    if product_option.isdigit():
        print(df.head(int(product_option)))
    else:
        print(df[df['name'].str.contains(product_option, case=False)])

    pass


# Display Functions
def first_oec():
    """ This is not the most general OEC caller we could write but it is one of them. """
    options = input(
        "Please enter the codes for the country, product and year you would like to search for in that order with a space in between: ")
    options_list = options.split()
    country = options_list[0]
    product = options_list[1]
    year = options_list[2]

    df_exp = TradeSet('hs92', 'export', year, country, 'show', product).visdf(6)
    df_imp = TradeSet('hs92', 'import', year, country, 'show', product).visdf(6)

    pass


# OEC API Class and associated functions
class TradeSet:
    """ A class to visualise OEC Data. """
    """
    We have a set of questions that we could ask the API, Most are nonsense, but these ones work:
    'Country' 'Destination' 'Product'
    gbr all show - What does gbr ixport?
    gbr show all - Where does gbr ixport?
    gbr show pro - Where does gbr ixport pro?
    gbr svn show - What does gbr ixport with svn?
    show all pro - Which countries ixport pro?
    show show pro - Which countries ixport pro? Although not loading
    all all show - What does the world ixport?
    all show all - Where does the world ixport?
    all show pro - Where does the world ixport pro?
    all svn show - What does the world ixport with svn?
    """

    def __init__(self, classification, trade_flow, year, origin, destination, product):
        self.params = {'classification': classification,
                       'trade_flow': trade_flow,
                       'year': year,
                       'origin': origin,
                       'destination': destination,
                       'product': product}
        self.trade_flow = trade_flow
        self.origin = origin
        self.destination = destination
        self.product = product
        self.classification = classification

        if (self.origin == 'show' and self.destination != 'show' and self.product != 'show'):
            self.show = 'origin_id'
        elif (self.origin != 'show' and self.destination == 'show' and self.product != 'show'):
            self.show = 'dest_id'
        elif (self.origin != 'show' and self.destination != 'show' and self.product == 'show'):
            self.show = self.classification + '_id'
        else:
            raise ValueError(
                'Origin, Destination or Product should read -show-, and no more than one of them')

    def tradejson(self):
        return oec.get_trade(**self.params)

    def tradedf(self):
        """ Wipes out finer detail that I don't want. """
        if len(self.tradejson()) == 0:
            print('The OEC provides no trade data for this request.')
            return 0
        else:
            df = pd.DataFrame(self.tradejson())
            df = df[df[self.classification + '_id_len'] == 6]
            return df

    def total(self):
        """ Returns total of either import or export depending on trade_flow. """
        return self.tradedf()[self.trade_flow + '_val'].sum()

    def total_eng(self):
        """ Returns total, as above, in scientific notation. """
        return EngNumber(self.total())

    def printjson(self):
        """ Pretty prints the JSON. """
        with open('json_printout.txt', 'w') as outfile:
            json.dump(self.tradejson(), outfile, indent=4)

    def visdf(self, num_view):
        """ Returns a reduced DataFrame so that we can see the data. """
        df = self.tradedf()
        trade_flow_val = self.trade_flow + '_val'
        if trade_flow_val not in df.columns:
            print("The OEC provides no trade data for this {}.".format(trade_flow_val))
            return 0

        df = df.sort_values(by=[trade_flow_val], ascending=False)
        df = df[[self.show, trade_flow_val]].iloc[0:num_view]
        df = df.dropna()

        if self.show == 'origin_id' or self.show == 'dest_id':
            dict_name = 'country 5'
        elif self.show == 'hs92_id':
            dict_name = 'products tight'
        else:
            raise ValueError('Something wrong in setting the dictionary title.')

        column_trans = trans(df[self.show].to_list(), dict_name, 's2l')
        df.insert(1, self.show + '_trans', column_trans)
        df['per'] = df[trade_flow_val] / self.total()
        df['per'] = df['per'].apply(lambda x: format(x, ".1%"))
        df[trade_flow_val] = df[trade_flow_val].apply(
            lambda x: EngNumber(x, precision=1))
        question(self)
        print('The total', trade_flow_val, 'is', self.total_eng())
        print(df, '\n')

        return df


def question(trade):
    """ Provides the question we are asking from our dictionary of parameters """

    ori, des, pro = trade.origin, trade.destination, trade.product
    allshow = ('all', 'show')
    tfl = trade.trade_flow

    if trade.trade_flow == 'export':
        tdir = 'to'
    elif trade.trade_flow == 'import':
        tdir = 'from'

    if ori not in allshow:
        ori_trans = trans([ori], 'country 3', 's2l')[0]
    if des not in allshow:
        dest_trans = trans([des], 'country 3', 's2l')[0]
    if pro not in allshow:
        prod_trans = trans([pro], 'products loose', 's2l')[0]

    # ori = cou, des = all, pro = show 'What does cou ixport?'
    if ori not in allshow and des == 'all' and pro == 'show':
        string = "What does {} {}?".format(ori_trans, tfl)

    # ori = cou, des = show, pro = all 'Where does cou ixport?'
    elif ori not in allshow and des == 'show' and pro == 'all':
        string = 'Where does {} {} {}?'.format(ori_trans, tfl, tdir)

    # ori = cou, des = show, pro = pro 'Where does cou ixport pro?'
    elif ori not in allshow and des == 'show' and pro not in allshow:
        string = 'Where does {} {} {} {}?'.format(
            ori_trans, tfl, prod_trans, tdir)

    # ori = cou, des = cou, pro = show 'What does cou ixport with cou?'
    elif ori not in allshow and des not in allshow and pro == 'show':
        string = 'What does {} {} {} {}?'.format(
            ori_trans, tfl, tdir, dest_trans)

    # ori = show, des = all, pro = pro 'Which countries ixport pro?'
    elif ori == 'show' and des == 'all' and pro not in allshow:
        string = 'Which countries {} {}?'.format(tfl, prod_trans)

    # ori = all, des = all, pro = show 'What does the world ixport?'
    elif ori == 'all' and des == 'all' and pro == 'show':
        string = 'What does the world {}?'.format(tfl)

    # ori = all, des = show, pro = all 'Where does the world ixport?'
    elif ori == 'all' and des == 'show' and pro == 'all':
        string = 'Where does the world {} {}?'.format(tfl, tdir)

    # ori = all, des = show, pro = pro 'Where does the world ixport pro?'
    elif ori == 'all' and des == 'show' and pro not in allshow:
        string = 'Where does the world {} {} {}?'.format(tfl, prod_trans, tdir)

    # ori = all, des = cou, pro = show 'What does the world ixport with cou?'
    elif ori == 'all' and des not in allshow and pro == 'show':
        string = 'What does the world {} {} {}?'.format(tfl, tdir, dest_trans)

    else:
        string = 'Unrecognised Question'

    print(string)

    return string


def trans(trans_in, dict_code, direction):
    """ Translates using dictionary from short to long or long to short. """

    if dict_code == 'country 5':
        dict_name = './datasets/oec_country_names.tsv'
        sma, lon = 'id', 'name'
    elif dict_code == 'country 3':
        dict_name = './datasets/oec_country_names.tsv'
        sma, lon = 'id_3char', 'name'
    elif dict_code == 'products tight':
        dict_name = './datasets/oec_products_hs_92.tsv'
        sma, lon = 'id', 'name'
    elif dict_code == 'products loose':
        dict_name = './datasets/oec_products_hs_92.tsv'
        sma, lon = 'hs92', 'name'
    else:
        raise ValueError('dict_code value has an error.')

    df = pd.read_csv(dict_name, delim_whitespace=True)
    if direction == 's2l':
        x, y = sma, lon
    elif direction == 'l2s':
        x, y = lon, sma
    else:
        raise ValueError('Direction value has an error.')

    n = len(trans_in)
    trans_out = [0] * n

    for i in range(0, n):
        df_mini = df[df[x] == trans_in[i]]
        if df_mini.shape[0] == 1:
            trans_out[i] = df_mini[y].tolist()[0]
        else:
            raise TypeError(
                'The dictionary was either found to have non-unique relations, or no relations at all.')

    return trans_out
