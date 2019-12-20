from ABNBRooms import ABNBRooms

counties = ["Alenquer", "Amadora", "Arruda dos Vinhos", "Azambuja", "Cadaval", "Cascais", "Lisboa", "Loures", "Lourinhã", "Mafra", "Odivelas","Oeiras", "Sintra", "Sobral de Monte Agraço", "Torres Vedras", "Vila Franca de Xira"]

for county in counties:

    print("starting county " + county)

    abnb = ABNBRooms(county, totalItems = 1000)

    #5 noites 1ª semana agosto
    abnb.checkin="2019-08-01"
    abnb.checkout="2019-08-06"
    #casal
    abnb.adults = 2

    roomList = abnb.getListings()

    df = roomList.toPandasDF()

    df.to_pickle("data\\"+county+".pkl")
