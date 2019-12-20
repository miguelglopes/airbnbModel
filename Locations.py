
from HttpRequest import httpRequest
from math import radians, cos, sin, asin, sqrt
from lxml import html

# This class has all the methods to take care of location data
# To find the county of a location string, we only need Location([locationString]).county
# to find the dsitance between 2 coordinates call Location.getDistance([lat1], [long1], [lat2], [long2])
class Location:

    __googleBaseUrl = "https://maps.googleapis.com/maps/api/geocode/json?"
    __codigoPostalUrl = "https://www.codigo-postal.pt"
    __counties = None
    __changeThis = {"alfama":"lisboa",
                    "bairro alto":"lisboa",
                    "são joão do estoril":"cascais",
                    "são pedro do estoril":"cascais",
                    "r. da atalaia":"lisboa",
                    "belém":"lisboa",
                    "ribamar, ericeira, portugal":"cascais",
                    "ramada, lisboa, portugal":"odivelas",
                    "costa da guia - torre, cascais, por":"cascais",
                    "costa da caparica":None,
                    "almada":None,
                    "samora correia":None,
                    "vale da pedra":None,
                    "salvaterra de magos":None,
                    "aldeia de juzo":None,
                    "alcochete":None,
                    "casal novo":None,
                    "peniche, portugal":None,
                    "atouguia da baleia":None,
                    "caldas da rainha":None,
                    "ferrel":None,
                    "nadadouro":None,
                    "foz do arelho":None,
                    "baleal":None,
                    "gaeiras":None,
                    "foz do arelho":None,
                    "óbidos municipality":None,
                    "óbidos municipality":None,
                    "foz do arelho":None,
                    "amoreira":None,
                    "casal moinho":None,
                    "póvoa de além":None,
                    "q.ta de santo antónio":None,
                    "terreiro d. joão v":None,
                    "portugal":None,
                    "pt": None,
                    "carvalhal":None,
                    "praia da areia branca":"lourinha",
                    "usseira":None
                    }

    
    def __init__(self, searchString):
        self.search = searchString #string
        if searchString in Location.__changeThis:
            self.county = Location.__changeThis[searchString]
            return
        self.name = None #string
        self.county= None
        self.longitude = None
        self.latitude = None
        self.__params = {}

        self.__searchLocation()

    #search location in google maps api
    def __searchLocation(self):

        #search google
        self.__buildParameters()

        response = httpRequest(self.__googleBaseUrl, self.__params)
        
        try:
            jsonData = response.json()["results"][0]
            self.longitude = jsonData["geometry"]["location"]["lng"]
            self.latitude = jsonData["geometry"]["location"]["lat"]
            self.name = jsonData["address_components"][0]["short_name"]
        except:
            return

        self.searchCounty()

    def searchCounty(self):

        if self.name.lower() in Location.__changeThis:
            self.county = Location.__changeThis[self.name.lower()]
            return

        #search concelhos e freguesias if doesnt existe
        if not Location.__counties:
            try:
                Location.__counties = {}
                response = httpRequest(Location.__codigoPostalUrl+"/distrito-lisboa/", None)
                concelhosData = html.fromstring(response.text) #get htmlData from string
                concelhos = concelhosData.xpath('//div[@class="placelist"]//a/@href') #get everything inside the wanted script tag

                for concelho in concelhos:
                    response = httpRequest(Location.__codigoPostalUrl+concelho, None)
                    freguesiasData = html.fromstring(response.text) #get htmlData from string
                    freguesias = freguesiasData.xpath('//ul[@class="list-unstyled list-inline"]//a/@href') #get everything inside the wanted script tag
                    Location.__counties[concelho.replace("/", "")] = []
                    for freguesia in freguesias:
                        Location.__counties[concelho.replace("/", "")].append(freguesia.replace(concelho, "").replace("/", ""))
            except:
                return None

        ldmin = 5
        for concelho in Location.__counties:
            ld = Location.__levenshteinDistance(self.name, concelho)
            if ld < ldmin:
                ldmin = ld
                self.county = concelho.lower()
            for freguesia in Location.__counties[concelho]:
                ld = Location.__levenshteinDistance(self.name, freguesia)
                if ld < ldmin:
                    ldmin = ld
                    self.county = concelho.lower()
                    
    @staticmethod
    def __levenshteinDistance(s, t):

        s1=s.replace(" ", "").replace(".", "").replace("-", "").replace("municipality","").lower().split(",", 1)[0]
        s2=t.replace(" ", "").replace(".", "").replace("-", "").replace("municipality","").lower().split(",", 1)[0]

        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2+1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]

    def __buildParameters(self):

        self.__addParameter("address", self.search)

        #default
        self.__addParameter("key", "AIzaSyBO6dxisfE9DnKLfNsd2cfVtvKLQo0LLhw")

    def __addParameter(self, parameterName, parameterValue):
        if parameterValue != None:
            self.__params[parameterName]=str(parameterValue)

    #convert location object to json
    def toJson(self):
        return {self.search : self.county}

    #static method to get distance between 2 locations. Implementation of Haversine formula
    @staticmethod
    def getDistance(lati1, long1, lati2, long2):

        # degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [long1, lati1, long2, lati2])

        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # Radius of earth in kilometers
        return c * r

        return c