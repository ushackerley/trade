from oec_script import oec_start
from fao_script import fao_start


def trade_start():
    """ This is the starter function to start exploring our datasets."""
    ans = True
    while ans:
        ans = input("""
            Which data sets would you like to explore?
			[1] FAO
			[2] COMTRADE via OEC
			[q] Quit
			""")
        if ans == "1":
            fao_start()
            # pass
        elif ans == "2":
            oec_start()
            # pass
        elif ans == "q":
            ans = False
        else:
            print("Sorry, I didn't understand")
            trade_start()

    pass


trade_start()
