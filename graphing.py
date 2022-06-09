# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 18:29:48 2022

@author: Felix
"""
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import csv
import mplcursors


# cluster name x y
totalClusters = 200

with open('Clusters_with_labels.csv') as f:
    reader = csv.reader(f)
    full_table = list(reader)
# full_table = pd.read_csv('Clusters_with_labels.csv')

cmap = matplotlib.cm.get_cmap('turbo')

colors = {}
for i in range(totalClusters):
    colors[i] = cmap(.005)

comparator = '1'
genre = []
x = []
y = []

for i, row in enumerate(full_table):
    cluster = row[0]
    j = 0
    if cluster == comparator:
        genre.append(row[1])
        x.append(int(row[2]))
        y.append(int(row[3]))
        j = j + 1

    else:
        minX1 = x.index(min(x))
        minY1 = y.index(min(y))
        maxX1 = x.index(max(x))
        maxY1 = y.index(max(y))
        fig, ax = plt.subplots()

        sc = plt.scatter(x, y, cmap=cmap)

        plt.scatter(x[minX1], y[minX1], color='red')
        plt.scatter(x[minY1], y[minY1], color='red')
        plt.scatter(x[maxX1], y[maxX1], color='red')
        plt.scatter(x[maxY1], y[maxY1], color='red')

        annot = ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        plt.title("Cluster: " + comparator)
        plt.show()
        # mplcursors.cursor()
        mplcursors.cursor(ax, hover=True).connect(
            "add", lambda sel: sel.annotation.set_text(genre[sel.index]))
        j = 0
        plt.annotate(genre[minX1], xy=(x[minX1], y[minX1]),
                     xytext=(x[minX1] + 30, y[minX1]), color='red', bbox=dict(
            boxstyle="round, pad=.3", fc="white", ec='red', lw=2),
            arrowprops=dict(arrowstyle="-|>",
                            connectionstyle="arc3,rad=-0.2", fc="white", color="red")
        )

        plt.annotate(genre[minY1], xy=(x[minY1], y[minY1]),
                     xytext=(x[minY1], y[minY1] + 30), color='red', bbox=dict(
            boxstyle="round, pad=.3", fc="white", ec='red', lw=2),
            arrowprops=dict(arrowstyle="-|>",
                            connectionstyle="arc3,rad=-0.2", fc="white", color="red")
        )

        plt.annotate(genre[maxX1], xy=(x[maxX1], y[maxX1]),
                     xytext=(x[maxX1] - 30, y[maxX1]), color='red', bbox=dict(
            boxstyle="round, pad=.3", fc="white", ec='red', lw=2),
            arrowprops=dict(arrowstyle="-|>",
                            connectionstyle="arc3,rad=-0.2", fc="white", color="red")
        )

        plt.annotate(genre[maxY1], xy=(x[maxY1], y[maxY1]),
                     xytext=(x[maxY1], y[maxY1] - 30), color='red', bbox=dict(
            boxstyle="round, pad=.3", fc="white", ec='red', lw=2),
            arrowprops=dict(arrowstyle="-|>",
                            connectionstyle="arc3,rad=-0.2", fc="white", color="red")
        )

        plt.savefig(f"Cluster_{comparator}.png")

        comparator = cluster
        genre.clear()
        x.clear()
        y.clear()


'''



        j = j+1
        if j % 10 == 0 and j < len(genre):
            label = ax.text(x, y, genre[j], bbox=dict(
                boxstyle="round, pad=.3", fc="white", ec=colors[i], lw=2))


            # Only works with annotations
            arrowprops=dict(arrowstyle="simple",
                            connectionstyle="arc3,rad=-0.2"))

def animate(j):
    for i, a in enumerate(ann_list):
        a.remove()
    ann_list[:] = []

    n = np.random.rand(5)*6
    scat.set_offsets([(r, f(r)) for r in n])
    for j in range(len(n)):
        ann = plt.annotate("{:.2f}".format(n[j]), xy = (
            n[j],f(n[j])), color = "purple", fontsize = 12)
        ann_list.append(ann)

ani = matplotlib.animation.FuncAnimation(fig, animate, frames=20, interval=360)
ani.save(__file__+".gif",writer='imagemagick', fps=3)
plt.show()


        # plt.scatter(x[minX1], y[minX1], color='red')
        # plt.scatter(x[minY1], y[minY1], color='red')
        # plt.scatter(x[maxX1], y[maxX1], color='red')
        # plt.scatter(x[maxY1], y[maxY1], color='red')

        # plt.annotate(genre[minX1], xy=(x[minX1], y[minX1]),
        #              xytext=(x[minX1] + 30, y[minX1]), color='red', bbox=dict(
        #              boxstyle="round, pad=.3", fc="white", ec='red', lw=2),
        #              arrowprops=dict(arrowstyle="-|>",
        #                              connectionstyle="arc3,rad=-0.2", fc="white", color="red")
        #              )

        # plt.annotate(genre[minY1], xy=(x[minY1], y[minY1]),
        #              xytext=(x[minY1], y[minY1] + 30), color='red', bbox=dict(
        #              boxstyle="round, pad=.3", fc="white", ec='red', lw=2),
        #              arrowprops=dict(arrowstyle="-|>",
        #                              connectionstyle="arc3,rad=-0.2", fc="white", color="red")
        #              )

        # plt.annotate(genre[maxX1], xy=(x[maxX1], y[maxX1]),
        #              xytext=(x[maxX1] - 30, y[maxX1]), color='red', bbox=dict(
        #              boxstyle="round, pad=.3", fc="white", ec='red', lw=2),
        #              arrowprops=dict(arrowstyle="-|>",
        #                              connectionstyle="arc3,rad=-0.2", fc="white", color="red")
        #              )

        # plt.annotate(genre[maxY1], xy=(x[maxY1], y[maxY1]),
        #              xytext=(x[maxY1], y[maxY1] - 30), color='red', bbox=dict(
        #              boxstyle="round, pad=.3", fc="white", ec='red', lw=2),
        #              arrowprops=dict(arrowstyle="-|>",
        #                              connectionstyle="arc3,rad=-0.2", fc="white", color="red")
        #              )

'''
