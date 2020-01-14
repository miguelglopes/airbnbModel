from enum import Enum
from ABNBRoom import ABNBRoom
from HttpRequest import httpRequest
import random
from lxml import html
from HttpRequest import httpRequest
import json
from datetime import datetime
import pandas

class SearchType(Enum):
    Home = "homes"
    Experiences = "experiences"

class RoomTypes(Enum):
    sharedRoom = "Shared room"
    hotelRoom = "Hotel room"
    privateRoom = "Private room"
    entireHome = "Entire home/apt"

#The class is instantiated and the user can choose to set, or not, multiple query parameters.
# Then the user has to call getListings() to start the search.
# This public method is where the first request is performed.
# After getting the roomIDs, the __getRooms private method is called from within, and it loops
# through all the roomsIDs and instantiates an ABNBRoom for each one, adding it to the instance of ABNBRooms.
# Finally, the user has the possibility of calling toPandasDF(), which transforms the list of ABNBRoom
# to a pandas dataframe.

class ABNBRooms(list):

    __baseURL = "https://www.airbnb.com/api/v2/explore_tabs"

    def __init__(self, place, homeType = SearchType.Home, totalItems =20):
        self.type = homeType #type of search. By default, home. Currently not being used
        self.query = place #string

        self.__params = {} #dictionary

        #optional. User must specify values if desired
        self.checkin = None #date
        self.checkout = None #date
        self.roomTypes = None #user should choose class. Can be a list. None means all. Needs to be the value
        self.priceMin = None #numeric
        self.priceMax= None #numeric
        self.adults = None #integer
        self.children = None #integer
        self.infants = None #integer
        self.workTrip=None #boolean
        self.immediateReservation = None #boolean
        self.__itemsNumber = 0 #int max 50. Next 50 use offset
        self.__itemsOffset = 0 #int
        self.__totalItems = totalItems #int

    def getListings(self):

        i=0

        #we can only get 50 at most. So loop 50+50+50... until totalitems
        while i <= (self.__totalItems-1)//50:

            self.__itemsOffset=i*50
            self.__itemsNumber=50
            if self.__itemsNumber >= self.__totalItems/(i+1):
                self.__itemsNumber = self.__totalItems - i*50

            print(str(self.__itemsOffset) + " " + str(self.__itemsNumber))

            self.__buildParameters()

            response = httpRequest(self.__baseURL, self.__params, debug=True)
            
            if response == None:
                print("ABNB could not be reached.")
                continue

            #requests.response has a json method, that works if the content is a json
            sections = response.json()["explore_tabs"][0]["sections"]
            dataToParse = {}

            for section in sections:
                if "listings" in section: #one of the sections has the __itemsNumber. But it may have more sections with a few more listings. I don't know why...
                    listings = section["listings"]
                    for listing in listings:
                        dataToParse[str(listing["listing"]["id"])] = {"jsonData":listing, "params":self.__params}

            #this json has much more information than the id. We gonna send it to our parser
            self.__getRooms(dataToParse) # we need to pass params in order to have checkin, checkout, etc
            
            i+=1

        return self

    def __buildParameters(self):

        self.__addParameter("query", self.query)
        self.__addParameter("checkin", self.checkin)
        self.__addParameter("checkout", self.checkout)
        self.__addParameter("room_types[]", self.roomTypes)
        self.__addParameter("price_min", self.priceMin)
        self.__addParameter("price_max", self.priceMax)
        self.__addParameter("adults", self.adults)
        self.__addParameter("children", self.children)
        self.__addParameter("infants", self.infants)
        self.__addParameter("infants", self.infants)
        self.__addParameter("work_trip", self.workTrip)
        self.__addParameter("ib", self.immediateReservation)
        self.__addParameter("items_per_grid", self.__itemsNumber)
        self.__addParameter("items_offset", self.__itemsOffset)


        #default
        self.__addParameter("_format", "for_explore_search_web")
        self.__addParameter("key", "d306zoyjsyarp7ifhu67rjxn52tv0t20")
        self.__addParameter("currency", "EUR")
        self.__addParameter("refinement_paths[]", "/homes")
        self.__addParameter("selected_tab_id", "home_tab")

    def __addParameter(self, parameterName, parameterValue):
        if parameterValue != None:
            self.__params[parameterName]=str(parameterValue)
    
    def __getRooms(self, dataToParse):
        #dataToParse is an object like the following:
        #{"1234":{"jsonData":{...}, "params":{...}}} where 1234 is the id
        
        #iterate over ids
        for id in dataToParse:

            print("Starting id=" + str(id))

            #create ABNBRoom Object and send it the data
            roomOb=ABNBRoom(id,  dataToParse[id]["params"], dataToParse[id]["jsonData"])

            #add roomObject to roomsList
            self.append(roomOb)

    def toPandasDF(self):
        return pandas.DataFrame.from_records([d.toDictionary() for d in self])