import random
from lxml import html
from HttpRequest import httpRequest
import json
from datetime import datetime
import pandas

# When ABNBRoom is instantiated, the __fillRoomInfo() is automatically called and performs, essentially, 3 tasks: 
# gettingdata from the initial json (search), getting data from the 2nd request (room info) and getting data from 
# the third request (reviews). There is also a public method, toDictionary(), that transforms the class to a dictionary, 
# which is needed to then transform ABNBRooms to a pandas dataframe.
class ABNBRoom:

    __baseURLMain = "https://www.airbnb.com/rooms/"
    __baseURLReviews = "https://www.airbnb.com/api/v2/homes_pdp_reviews"

    def __init__(self, id, params = {}, evenMoreData = None):
        # params is optional, allows passing checkin, checkout etc. Its ok if there are too many, the yare ignored
        #dataToParse is an object like the following:
        #{"1234":{"jsonData":{...}, "params":{...}}} where 1234 is the id

        self.id = id
        self.__params = params
        self.__evenMoreData = evenMoreData

        self.rating = None #float
        self.minNights = None #int
        self.isSuperHost = None #boolean
        self.isVerified = None #boolean
        self.allowsPets = None #boolean
        self.allowsChildren = None #boolean
        self.allowsInfants = None #boolean
        self.allowsSmoking = None #boolean
        self.allowsEvents = None #boolean
        self.latitude = None #float
        self.longitude = None #float
        self.checkinRating = None #float
        self.cleanlinessRating = None #float
        self.communicationRating = None #float
        self.isInstantBookPossible = None #boolean
        self.locationRating = None #float
        self.personCapacity = None #int
        self.isHotel = None #Boolean
        self.lastUpdate = None #Date
        self.hostDate = None #Date
        self.name = None #str
        self.accuracyRating = None #int
        self.bathrooms = None #int
        self.bedrooms = None #int
        self.beds = None #int
        self.pictureCount = None #int
        self.isBusinessTravel = None #boolean
        self.isFullyRefundable = None #boolean
        self.ratePerNight = None #float
        self.totalPrice = None #float
        self.serviceFee = None #float
        self.roomType = None #str
        self.monthlyPriceFactor = None #float
        self.responseRate = None #float
        self.responseTime = None #float
        self.reviewsCount = None #int
        self.ratingC = None #float


        self.checkin = self.__params["checkin"] #string
        self.checkout = self.__params["checkout"] #string

        self.location = None #str
        self.country = None #str
        self.amenities = []
        self.languages = []
        self.reviews = []

        url = self.__baseURLMain + str(self.id)
        response = httpRequest(url, self.__params, debug=True)
        if response is not None:
            self.__fillRoomInfo(response)
            self.url = response.url #save the final url with params

    #performs, essentially, 3 tasks: 
    # gettingdata from the initial json (search), getting data from the 2nd request (room info) and getting data from the third request (reviews)
    def __fillRoomInfo(self, response):
            htmlData = html.fromstring(response.text) #get htmlData from string
            jsonData = htmlData.xpath('//script[@data-state="true" and @type="application/json"]')[0] #get everything inside the wanted script tag
            jsonData = jsonData.text.replace("<!--", "").replace("-->", "") #get Json data as String
            jsonData = json.loads(jsonData) # convert json string to actual json, ie, dictionary
            jsonData = jsonData["bootstrapData"]["reduxData"]["homePDP"]["listingInfo"]["listing"]

            #get Parameters From Json
            self.rating = self.__getKeyValue(jsonData,"star_rating")
            self.minNights = self.__getKeyValue(jsonData,"min_nights")
            self.isSuperHost = self.__getKeyValue(jsonData["primary_host"],"is_superhost")
            self.isVerified = self.__getKeyValue(jsonData["primary_host"],"identity_verified")
            self.allowsPets = self.__getKeyValue(jsonData["guest_controls"],"allows_pets")
            self.allowsChildren = self.__getKeyValue(jsonData["guest_controls"],"allows_children")
            self.allowsInfants = self.__getKeyValue(jsonData["guest_controls"],"allows_infants")
            self.allowsSmoking = self.__getKeyValue(jsonData["guest_controls"],"allows_smoking")
            self.allowsEvents = self.__getKeyValue(jsonData["guest_controls"],"allows_events")
            self.latitude = self.__getKeyValue(jsonData,"lat")
            self.longitude = self.__getKeyValue(jsonData,"lng")
            self.checkinRating = self.__getKeyValue(jsonData["p3_event_data_logging"],"checkin_rating")
            self.cleanlinessRating = self.__getKeyValue(jsonData["p3_event_data_logging"],"cleanliness_rating")
            self.communicationRating = self.__getKeyValue(jsonData["p3_event_data_logging"],"communication_rating")
            self.accuracyRating = self.__getKeyValue(jsonData["p3_event_data_logging"],"accuracy_rating")
            self.locationRating = self.__getKeyValue(jsonData["p3_event_data_logging"],"location_rating")
            self.personCapacity = self.__getKeyValue(jsonData["p3_event_data_logging"],"person_capacity")
            self.isHotel = self.__getKeyValue(jsonData,"is_hotel")
            
            try:
                self.lastUpdate = datetime.strptime(self.__getKeyValue(jsonData,"calendar_last_updated_at"),"%Y-%m-%d").strftime("%Y-%m-%d")
            except:
                self.lastUpdate = None
            try:
                self.hostDate = datetime.strptime(self.__getKeyValue(jsonData["primary_host"],"member_since"),"%B %Y").strftime("%Y-%m-%d")
            except:
                self.hostDate = None

            self.name = self.__getKeyValue(jsonData, "name")
            self.responseRate = self.__getKeyValue(jsonData["primary_host"],"response_rate_without_na")
            if self.responseRate != None:
                self.responseRate = self.responseRate.replace("%","")
            self.responseTime = self.__getKeyValue(jsonData["primary_host"],"response_time_without_na")#this is a string, not a number. Dont know how to parse TODO

            self.__getLocation(jsonData)
            self.__getCountry(jsonData)
            self.__getAmenities(jsonData)
            self.__getLanguages(jsonData)

            #get info from json evenMoreData -> this is the initial json, when we searched
            if self.__evenMoreData != None:
                self.ratingC = self.__getKeyValue(self.__evenMoreData["listing"],"avg_rating")
                self.reviewsCount = self.__getKeyValue(self.__evenMoreData["listing"],"reviews_count")
                self.bathrooms = self.__getKeyValue(self.__evenMoreData["listing"],"bathrooms")
                self.bedrooms = self.__getKeyValue(self.__evenMoreData["listing"],"bedrooms")
                self.beds = self.__getKeyValue(self.__evenMoreData["listing"],"beds")
                self.pictureCount = self.__getKeyValue(self.__evenMoreData["listing"], "picture_count")
                self.isBusinessTravel = self.__getKeyValue(self.__evenMoreData["listing"],"is_business_travel_ready")
                self.isFullyRefundable = self.__getKeyValue(self.__evenMoreData["listing"],"is_fully_refundable")
                self.isInstantBookPossible = self.__getKeyValue(self.__evenMoreData["pricing_quote"],"can_instant_book")
                self.ratePerNight = self.__getKeyValue(self.__evenMoreData["pricing_quote"]["rate_with_service_fee"],"amount")
                self.totalPrice = self.__getKeyValue(self.__evenMoreData["pricing_quote"]["price"]["total"],"amount")
                self.roomType = self.__getKeyValue(self.__evenMoreData["listing"],"room_type")
                self.monthlyPriceFactor = self.__getKeyValue(self.__evenMoreData["pricing_quote"],"monthly_price_factor") #idk what this is
                
                self.__getServiceFee(self.__evenMoreData["pricing_quote"]["price"]["price_items"])


            #main request has only 7 reviews, at most. We want more.
            self.__getReviews()
           
    def __getLocation(self, jsonData):
        try:
            temp = jsonData["location_title"]
            self.location = temp
        except:
            raise

    def __getCountry(self, jsonData):
        try:
            temp = jsonData["country_code"]
            self.country = temp
        except:
            raise

    def __getAmenities(self, jsonData):
        try:
            for amenity in jsonData["listing_amenities"]:
                if amenity["is_present"] == True:
                    temp = amenity["name"]
                    self.amenities.append(temp)
        except:
            raise

    def __getLanguages(self, jsonData):
        try:
            for lang in jsonData["primary_host"]["languages"]:
                self.languages.append(lang)
        except:
            raise

    def __getReviews(self):
        try:
            #default
            self.__params = {}
            self.__addParameter("locale", "en")
            self.__addParameter("key", "d306zoyjsyarp7ifhu67rjxn52tv0t20")
            self.__addParameter("listing_id", self.id)
            self.__addParameter("_format", "for_p3")
            self.__addParameter("limit", self.reviewsCount)
            response = httpRequest(self.__baseURLReviews, self.__params, debug=True)
            if response == None:
                print("ABNB could not be reached.")
                return

            #requests.response has a json method, that works if the content is a json
            reviews = response.json()["reviews"]
            for review in reviews:
                if "language" in review:
                    if review["language"]=="en":
                        self.reviews.append(review["comments"])

        except:
            print("error in reviews, but continue")

    def __addParameter(self, parameterName, parameterValue):
        if parameterValue != None:
            self.__params[parameterName]=str(parameterValue)

    def __getServiceFee(self, jsonData):
        try:
            for p in jsonData:
                if "service" in p["localized_title"].lower():
                    self.serviceFee = p["total"]["amount"]
                    break
        except:
            raise

    def __getKeyValue(self, data, key):
        if key in data:
            return data[key]
        else:
            return None

    def toDictionary(self):
        #modify internal method __dict__ to only return important information
        dic = self.__dict__

        if "_ABNBRoom__params" in dic:
            del dic["_ABNBRoom__params"]
        if "_ABNBRoom__baseURLMain" in dic: # i think this never happens since it's declared outside __init__
            del dic["_ABNBRoom__baseURLMain"]
        if "_ABNBRoom__evenMoreData" in dic:
            del dic["_ABNBRoom__evenMoreData"]
        if "_ABNBRoom__Locations" in dic:
            del dic["_ABNBRoom__Locations"]
        if "_ABNBRoom__Countries" in dic:
            del dic["_ABNBRoom__Countries"]
        if "_ABNBRoom__Amenities" in dic:
            del dic["_ABNBRoom__Amenities"]
        if "_ABNBRoom__Languages" in dic:
            del dic["_ABNBRoom__Languages"]

        return dic