import pygmt

def map_points(df, name): 
    region = [
        df.longitude.min() - 1,
        df.longitude.max() + 1,
        df.latitude.min() - 5,
        df.latitude.max() + 10,
        ]
    print(df.head())

    fig = pygmt.Figure()
    fig.basemap(region=region, projection="M8i", frame=True)
    fig.coast(land="black", water="skyblue")
    fig.plot(x=df.longitude, y=df.latitude, style="c0.3c", fill="black", pen="black")

    fig = pygmt.Figure()
    fig.basemap(region=region, projection="M8i", frame=True)
    #fig.coast(land="seagreen", water="white")
    fig.coast(land="lightblue", water="white")
    fig.plot(
        x=df.longitude,
        y=df.latitude,
        size=0.08 * df.counts,
        style="cc",
        fill="gray",
        pen="gray40",
    )
    fig.savefig("../data/" + name + ".jpg")
    
