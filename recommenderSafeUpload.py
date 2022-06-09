import sys
import mysql.connector
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.neighbors import KDTree
from sklearn.metrics import pairwise_distances_argmin_min
from collections import Counter
from collections import defaultdict
from datetime import datetime

testing = False
app_user = "0"
# TODO Take User tokens password use HarryTeeth
# Todo JsonAppsetings for this info
# TODO Scoped Sessions to help with code refactor and prevent passing db connections


def run_recommender(
    user,
    password,
    recommend_type,
    app_user_id,
    server="67.171.238.128",
    port="1123",
    database="test",
):
    if testing:
        user = "abc"
        password = "123"
    db = mysql.connector.connect(
        host=server, port=int(port), database=database, user=user, password=password
    )
    spotify_user_query(dbconnection=db, user=app_user_id)

    db.close()


def clusterGraph(
    x_location,
    y_location,
    genre_labels,
    fileName,
    numberOfClusters,
    xMin,
    xMax,
    yMin,
    yMax,
    size,
    plot=False,
):

    coordinates = np.array(list(zip(x_location, y_location)))

    xyKmeans = KMeans(n_clusters=numberOfClusters).fit(coordinates)
    labels = xyKmeans.fit_predict(coordinates)

    color_theme = np.unique(labels)
    cluster_centers = xyKmeans.cluster_centers_
    # Dark mode, incomplete good for slides though
    # plt.rcParams['figure.facecolor'] = 'black'
    # plt.rcParams['axes.facecolor'] = 'black'

    plt.figure(figsize=(15, 15), dpi=60)
    # argminndarray

    # Y[argmin[i], :] is the row in Y that is closest to X[i, :].
    closest, _ = pairwise_distances_argmin_min(cluster_centers, coordinates)

    # intermediate get all events and genres figure out where they live
    # Uncomment for overall graphs

    # -40 is good for small graph too big for big graph More Negative
    # Add Title
    # Add User ave for user Graph
    # Maybe User Ave on big graph
    plot = False
    if plot:
        for i in color_theme:
            plt.scatter(
                coordinates[labels == i, 0],
                coordinates[labels == i, 1],
                label=i,
                s=size,
            )
        # plt.scatter(cluster_centers[:,0], cluster_centers[:,1], s = 80, color = 'k')
        plt.xlim(int(xMin - (xMin * 0.2)), int(xMax + (xMax * 0.2)))
        plt.ylim(int(yMin - (yMin * 0.2)), int(yMax + (yMax * 0.2)))

        ax = plt.gca()
        ax.axes.xaxis.set_ticks([])
        ax.axes.yaxis.set_ticks([])

        # This is meant to be User values, userAveX userAveY
        # plt.scatter(userX, userY, c='r', marker = "*", s = 10)
        plt.title("All Genres")
        plt.text(100, -1200, "Denser/Atmospheric")
        plt.text(1000, -1200, "Spikier/Bouncier")
        # Minus 75 is good for big graph -3.5 is too much for small graph
        plt.text(-75, 100, "Organic", rotation=90)
        plt.text(-75, 15000, "Mechanical/Electric", rotation=90)

        plt.show()
    return coordinates[closest], coordinates[:, 0], coordinates[:, 1], labels

    """but in general down is more organic, up is more mechanical and electric; left is denser and more atmospheric, right is spikier and bouncier."""


# Scope cid secret redirect not required, Removed spotipy


def spotify_user_query(
    dbconnection,
    user,
    cid="",
    secret="",
    scope="user-library-read user-top-read",
    redirect="http://localhost",
    updateClusters=False,
    updateEventClusterId=True,
):

    cursor = dbconnection.cursor()
    if user == "":
        user = "MIKESWENSONISAWESOME"
    sql = f"""SELECT Name, X,Y from capstone.Genres 
    inner join capstone.GenreMetadatas on capstone.Genres.Id = capstone.GenreMetadatas.GenreId;"""

    # Name, x, y
    full_genre_map = []
    full_coordinates = cursor.execute(sql)
    for genre_data in cursor:
        full_genre_map.append(genre_data)
    numberOfGenres = len(full_genre_map)

    # Normalize X,Y Range
    x_location = [round(num[1] * 2) for num in full_genre_map]
    y_location = [round(num[2] / 4) for num in full_genre_map]
    genre_labels = [num[0] for num in full_genre_map]

    # Could pass in x_location, y_location
    xy_FullGenre = [
        tuple((round(num[1] * 2), round(num[2] / 4))) for num in full_genre_map
    ]

    x_min = min(x_location)
    y_min = min(y_location)

    x_max = max(x_location)
    y_max = max(y_location)
    clusterContains = []

    # Needs to be a passable
    selectedNumberOfClusters = 200

    cluster_centers, x_list, y_list, labels = clusterGraph(
        x_location,
        y_location,
        genre_labels,
        "FullGraph",
        selectedNumberOfClusters,
        x_min,
        x_max,
        y_min,
        y_max,
        size=6,
        plot=False,
    )

    xy_clusterContains = []

    if len(labels) == len(full_genre_map):
        for i in range(len(labels)):
            # x,y,clusterId, genreName
            clusterContains.append((x_list[i], y_list[i], labels[i], genre_labels[i]))
            xy_clusterContains.append((x_list[i], y_list[i]))
    changed = True

    # Added Clusters to table Cluster 0 is cluster 52 due to mysql not liking ID 0

    if updateClusters:
        cluster_centroids_labels = []
        for index, i in enumerate(range(len(cluster_centers))):
            for j in range(len(clusterContains)):
                if (
                    cluster_centers[i][0] == clusterContains[j][0]
                    and cluster_centers[i][1] == clusterContains[j][1]
                ):
                    if clusterContains[j][2] == 0:
                        temp = list(clusterContains[j])
                        temp[2] = selectedNumberOfClusters
                        clusterContains[j] = temp
                    cluster_centroids_labels.append(
                        (
                            cluster_centers[i][0],
                            cluster_centers[i][1],
                            clusterContains[j][2],
                        )
                    )
                    sql = f"""Insert into capstone.Clusters (Id, X, Y) values ({clusterContains[j][2]}, {cluster_centers[i][0]}, {cluster_centers[i][1]}) 
                              ON DUPLICATE KEY Update capstone.Clusters.X = {cluster_centers[i][0]}, capstone.Clusters.Y = {cluster_centers[i][1]} ;"""
                    result = cursor.execute(sql)
                    dbconnection.commit()
    sql = "Select * From Clusters"
    dbClusters = {}
    cursor.execute(sql)
    for row in cursor:
        dbClusters[row[0]] = tuple((row[1], row[2], []))
    if updateClusters:
        for i in range(len(clusterContains)):
            if clusterContains[i][2] == 0:
                temp = list(clusterContains[i])
                temp[2] = selectedNumberOfClusters
                clusterContains[i] = temp
            sql = f"""Update capstone.Genres set ClusterId = {clusterContains[i][2]} where capstone.Genres.Name = %s"""
            name = (full_genre_map[i][0],)
            cursor.execute(sql, name)
            dbconnection.commit()
    # Genre Name, Event Id
    sql = """SELECT EventsId,ClusterId FROM capstone.EventGenre join capstone.Genres on capstone.EventGenre.GenresId = capstone.Genres.Id Order by Name Asc;"""

    # This will not be scalable, needs to be translated to SQL for speedup
    eventAssignments = defaultdict(list)
    cursor.execute(sql)
    for clusterId in cursor:
        eventAssignments[clusterId[0]].append(clusterId[1])
    eventAssignmentMajority = {}
    for event in eventAssignments:
        c = Counter(eventAssignments[event])
        value = c.most_common()[0][0]
        eventAssignmentMajority[event] = value
    sqlParameters = []
    index = 0

    # ########## CLEAR USER RECOMMENDATIONS ####################
    cursor.execute(
        f"""Delete From capstone.UserRecommendations where UserRecommendations.ApplicationUserId = '{user}' """
    )
    dbconnection.commit()

    if updateClusters:
        # Delete everything that is associated with a cluster ID
        cursor.execute("Select Count(*) from UserRecommendations;")
        for row in cursor:
            entries = row
        for i in range(entries[0]):
            cursor.execute("DELETE FROM UserRecommendations LIMIT 1;")
            dbconnection.commit()
        cursor.execute("Select Count(*) from capstone.ApplicationUserCluster;")
        for row in cursor:
            entries = row
        for i in range(entries[0]):
            cursor.execute("DELETE FROM capstone.ApplicationUserCluster LIMIT 1;")
            dbconnection.commit()
        cursor.execute("Select Count(*) from capstone.ClusterEvent;")
        for row in cursor:
            entries = row
        for i in range(entries[0]):
            cursor.execute("DELETE FROM capstone.ClusterEvent LIMIT 1;")
            dbconnection.commit()
    if updateEventClusterId:
        for key in eventAssignments.keys():
            for clusterId in eventAssignments[key]:
                cursor.execute(
                    f"""Insert into capstone.ClusterEvent(ClustersId, EventsId) Values ({clusterId},{key}) ON DUPLICATE KEY
                               Update capstone.ClusterEvent.EventsId = {key};"""
                )
                dbconnection.commit()
                # Execute Many if we end up with a load of events
    # Could just grab the sums here
    # Do Sums and Where Username == Passed in User
    sql = f"""SELECT ANU.Id AS Username, Genres.Name, GenreMetadatas.X, GenreMetadatas.Y  FROM ArtistUserMusicData
            LEFT JOIN Artists A ON ArtistUserMusicData.ArtistsId = A.Id
            LEFT JOIN UserMusicDatas UMD on ArtistUserMusicData.UserMusicDataId = UMD.Id
            LEFT JOIN AspNetUsers ANU on UMD.UserMetadataId = ANU.UserMetadataId
            LEFT JOIN ArtistGenre AG on A.Id = AG.ArtistsId
            LEFT JOIN Genres on AG.GenresId = Genres.Id
            LEFT JOIN GenreMetadatas on GenreId = AG.GenresId
            where ANU.Id = '{user}'
            ORDER BY ANU.UserName, UMD.Type;"""

    # Possibly filter events by EVent Date > now()
    # Clear User recommendations
    # Possibly do this in the c#

    usersGenresXY = {}
    cursor.execute(sql)
    for row in cursor:
        if row[1] == None or row[2] == None:
            continue
        if row[0] in usersGenresXY.keys():
            count = usersGenresXY[row[0]][2]
            temp = tuple((row[2], row[3]))
            temp2 = tuple((usersGenresXY[row[0]][0], usersGenresXY[row[0]][1]))
            total = tuple((temp[0] + temp2[0], temp[1] + temp2[1], count + 1))
            usersGenresXY[row[0]] = tuple((total[0], total[1], total[2]))
        else:
            usersGenresXY[row[0]] = tuple((row[2], row[3], 1))
    usersNormalizedXY = {}
    for key in usersGenresXY.keys():
        divisor = usersGenresXY[key][2]
        usersNormalizedXY[key] = tuple(
            (
                round(usersGenresXY[key][0] / divisor),
                round(usersGenresXY[key][1] / divisor),
                [],
            )
        )
    # cluster XY
    dbClustersXY = []
    # Cluster Ids
    dbClusterLbls = []
    for key in dbClusters.keys():
        dbClusterLbls.append(key)
        dbClustersXY.append(tuple((dbClusters[key][0], dbClusters[key][1])))
    # 47 is 52 all other numbers = number - 1
    usersNormalizedXYList = {}
    usersNormalizedIds = {}
    for val, key in enumerate(usersNormalizedXY.keys()):
        usersNormalizedXYList[val] = tuple(
            (usersNormalizedXY[key][0], usersNormalizedXY[key][1])
        )
        usersNormalizedIds[val] = key
    userClusterSelected, _ = pairwise_distances_argmin_min(
        list(usersNormalizedXYList.values()), dbClustersXY
    )

    ClusterTree = KDTree(dbClustersXY, leaf_size=8)
    k = 10
    dist, ind = ClusterTree.query(list(usersNormalizedXYList.values()), k)

    userKDClusters = {}
    for index, key in enumerate(usersNormalizedXY):
        usersNormalizedXY[key][2].append(ind[index])
    sql = "Select * from ClusterEvent"
    cursor.execute(sql)
    for row in cursor:
        if row[0] not in userKDClusters.keys():
            userKDClusters[row[0]] = []
            userKDClusters[row[0]].append(row[1])
        else:
            userKDClusters[row[0]].append(row[1])
    event = []

    if updateEventClusterId:
        for userInfo in usersNormalizedXY:
            filterDuplicates = set()
            for clusterList in usersNormalizedXY[userInfo][2]:
                for clusterId in clusterList:
                    cursor.execute(
                        f"""Insert into capstone.ApplicationUserCluster (ClustersId, UsersId) Values ({int(clusterId)}, '{userInfo}') ON DUPLICATE KEY UPDATE ClustersId = {int(clusterId)}, UsersId = '{userInfo}' """
                    )
                    dbconnection.commit()
    if updateEventClusterId:
        for userInfo in usersNormalizedXY:
            for clusterList in usersNormalizedXY[userInfo][2]:
                for rank, clusterId in enumerate(clusterList):
                    if clusterId in userKDClusters.keys():
                        eventList = userKDClusters[clusterId]
                        # For event in eventList add to a set then push each event in set to db
                        for event in eventList:
                            filterDuplicates.add(event)
                for event in filterDuplicates:
                    created = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
                    # This is still f, everything gets the same rating
                    cursor.execute(
                        "Insert into capstone.UserRecommendations (ApplicationUserId, EventId, Score, CreatedDateTime) Values (%s,%s,%s,%s)",
                        tuple((userInfo, event, (rank + 1), created)),
                    )
                    dbconnection.commit()
    print("Finished")

    """
    #Plot stuff this was an interim local check
    
    f, diagram = plt.subplots()
    g, genre_weight = plt.subplots()
    #diagram.plot(x_location,y_location,'bo')
    #diagram.plot(x_ave,y_ave,'r*')
    #diagram.annotate("Your Average", (x_ave,y_ave))
    
    

    for index, point in enumerate(x_location):
          if(index % 5 == 0):
              diagram.annotate(genre_labels[index], (x_location[index], y_location[index]))
    bar_x_axis_pos = []

    tt = range(0, len(genre_labels), 1)
    bars = plt.bar(tt, usersTopGenres.values(), width = 0.5, align='center')    
    plt.xticks(tt, genre_labels, rotation = 90)
    plt.xlim(-1.0, 11.5)

    
    #jaccard_sim = len(keywordList.intersection(usersTopGenres)) / len(keywordList.union(usersTopGenres))
    plt.show()
    
    
    
    
    #Spotipy Notes
    #oauth2 does not require a redirect and user allowing access 
    scope = "user-library-read user-top-read"
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    
    
    #oauth2 does not require a redirect and user allowing access 
    token = spotipy.util.prompt_for_user_token(
                                       scope = scope,
                                       client_id = cid, 
                                       client_secret= secret,
                                       redirect_uri='http://www.google.com')
    
    usersTopGenres = {}
    
    if token:
        
         sp = spotipy.Spotify(auth=token)
         
         usersTopArtists = sp.current_user_top_artists(20, 0, "long_term")
         for index, artist in enumerate(usersTopArtists["items"]):
             for genre in usersTopArtists["items"][index]["genres"]:
                 if not genre in usersTopGenres:
                     usersTopGenres[genre] = 1
                 else:
                     usersTopGenres[genre] += 1
                
    else:
        print ("Can't get token for " + sp.me())
    """


if __name__ == "__main__":
    # database args
    if not testing:
        server = sys.argv[1]
        port = sys.argv[2]
        database = sys.argv[3]
        user = sys.argv[4]
        password = sys.argv[5]

        # recommendation specific data
        recommend_type = sys.argv[6]
        app_user_id = sys.argv[7]
        # print("reco for:" + app_user_id)

        run_recommender(
            server=server,
            port=port,
            database=database,
            user=user,
            password=password,
            recommend_type=recommend_type,
            app_user_id=app_user_id,
        )
    '''
                                       client_id = cid, 
                                       client_secret= secret,
                                       redirect_uri='http://www.google.com')
    
    usersTopGenres = {}
    
    if token:
        
         sp = spotipy.Spotify(auth=token)
         
         usersTopArtists = sp.current_user_top_artists(20, 0, "long_term")
         for index, artist in enumerate(usersTopArtists["items"]):
             for genre in usersTopArtists["items"][index]["genres"]:
                 if not genre in usersTopGenres:
                     usersTopGenres[genre] = 1
                 else:
                     usersTopGenres[genre] += 1
                
    else:
        print ("Can't get token for " + sp.me())
    """


if __name__ == "__main__":
    # database args
    if not testing:
        server = sys.argv[1]
        port = sys.argv[2]
        database = sys.argv[3]
        user = sys.argv[4]
        password = sys.argv[5]

        # recommendation specific data
        recommend_type = sys.argv[6]
        app_user_id = sys.argv[7]
        # print("reco for:" + app_user_id)

        run_recommender(
            server=server,
            port=port,
            database=database,
            user=user,
            password=password,
            recommend_type=recommend_type,
            app_user_id=app_user_id,
        )
'''
