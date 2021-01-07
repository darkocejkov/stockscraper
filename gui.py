#stdlibs
import requests
import time
import copy

#dependencies
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import Label, Tk, Button

#init root object for tkinter
root = tk.Tk()
root.title("STOCK FINDER")

# ---------- STATE FUNCTIONS ----------
def defineitemlabels(arr):
        #given a list of names, define the position of each label (col 0, row [1, n])
        il = []
        r = 1 #init row count
        for x in arr: #NOTE: not using StringVar objects, so we cannot change them in operation
            print(x)
            label = Label(root, text = x) #create unique label object with text as the name of product
            label.grid(row=r, column=0, pady = 10) #align it to grid (increasing vertically)
            il.append(label) #append label to array
            r+=1

        return il

def definelocationlabels(arr): #NOTE: not using StringVar objects, so we cannot change them in operation
    #given a list of locations, define the positions of each label (cols [1,n], row 0)
    ll = []
    c = 1 #init col count
    for x in arr:
        label = Label(root, text = x) #create unique label object
        label.grid(row=0, column=c, padx = 10)
        ll.append(label) #append label to an array
        c+=1
    
    return ll

def defineitemstocks(arr):
    #given a list of stocks per location, define positions of each label
    itemstocklabels = []
    stringarray = []
    a = 1
    
    for x in arr: #arr is a 2D array of [product, product, product ...] with each product = [stock loc 1, stock loc 2, ...]

        b = 1
        for y in x:
            var = tk.StringVar() #create StringVar object and set value as y, and use the stringvar as the variable for label text
            var.set(y) #this is done to be able to change/update the label value mid-operation
            label = Label(root, textvariable = var) 
            label.grid(row = a, column = b, padx = 10)
            stringarray.append(var) #append stringvars to array to be able to change them later on
            itemstocklabels.append(label)

            b += 1
        a += 1
    
    return stringarray
# ---------- END STATE FUNCTIONS ----------


# ---------- AUX FUNCTIONS -----------
def makestringvars(arr):
    z = []
    for x in arr:
        for y in x:
            vari = tk.StringVar() #this function is used to 'expand' the 2D array into a 1D array containing only stringvar objects
            vari.set(y)
            z.append(vari)

    return z

def plus(str):
    
    url = str.replace(" ", "+") #replace a given string's whitespaces with a plus, since the search query in URL is based on this format
    return url

# -------------- END AUX --------------

# ---------------

def scrapestock(item, locs):

    url = f'https://www.canadacomputers.com/search/results_details.php?language=en&keywords={plus(item)}'
    cc = requests.get(url)

    global solonames

    if cc.status_code == 200:
        soup = BeautifulSoup(cc.content, 'html.parser') #create BS object to parse the content of requested page

        prodlist = soup.find(id="product-list")

        names = []
        for product in prodlist.find_all("a", {"class": "text-dark text-truncate_3"}): #find all elements fitting the properties
            name = product.text
            names.append(name)

        solonames = copy.deepcopy(names) #create a copy of the names w/o other info.

        c = 1
        x = 0
        string = ""
        for allstocks in prodlist.find_all("div", {"class": "col-md-4 col-sm-6"}): #find stock levels for each product

            for loc in locs:

                stocks_of_loc = allstocks.find("a", text=loc)
                if stocks_of_loc is not None:
                    stock_div = (stocks_of_loc.find_parent('div')).find_parent('div') #find the double-parent of the div which is the element containing the stock-value per a specific location
                    stock = stock_div.find("span", {"class": "stocknumber"})
                    string += ("|" + loc + " ( " + stock.text + " )|")

                    if (c == len(locs)):
                        c = 1
                        names[x] += string
                        string = ""
                        x += 1
                    else:
                        c += 1

        stocksarray = [] #

        for name in names:
            
            name_stock = name.split("|")
            print(name_stock[0])
            
            
            i = len(locs)
            temp = [0]*i
            #print(i)
            for x in range(1, len(name_stock)): 
                print("\t" + name_stock[x])
                val = name_stock[x].split() #find the stock number from the split string
                
                #print(val)
                
                if(len(val) != 0):
                    ind = locs.index(val[0]) #find the index of the appropriate store location
                    temp[ind] = val[2] #val[2] is the appropriate stock level, and put that in the order
                    #stock_value = val[1]
                    #print("\t"+stock_value)
                    i -= 1 #decrease r by one since the order within the formatted string is reversed

            #print('r')
            #print(temp)

            stocksarray.append(temp) #stocks array holds stock values (for each spec. location) for each product
        
        #print(stocksarray)
    
    return stocksarray
# ----------

count = 0

def updatestock():

    global search_item
    global locations

    z = scrapestock(search_item, locations)

    y = makestringvars(z)

    global stocklabels
    global count

    for x in range(0, len(stocklabels)):
        stocklabels[x].set(y[x].get())

    count += 1
    count_var.set(str(count))

    #root.after(ms, updatestock) #NOTE: uncomment this line to have the window auto-update after 'ms' amount of time (in milliseconds)
        #do not put ms < 1000, as this may be too often and would be too slow to get data and update (not tested)



search_item = input("enter item to search within Canada Computers: ")
loc = input("enter locations split by a space: ")
locations = loc.split()

for x in range(0, len(locations)):
    locations[x] = locations[x].capitalize()    

z = scrapestock(search_item, locations)

namelabels = defineitemlabels(solonames)
loclabels = definelocationlabels(locations)

stocklabels = defineitemstocks(z)

count = 0
count_var = tk.StringVar()
count_var.set(str(count))

update_count = Button(root, textvariable = count_var, command=updatestock)
update_count.grid(row = 0, column = 0, padx = 10, pady = 10)

sample = [0] * len(stocklabels)


updatestock()

root.mainloop()