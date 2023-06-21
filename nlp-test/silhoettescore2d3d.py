import json
import numpy as np
import tkinter as tk
from tkinter import filedialog
from sklearn.metrics import silhouette_score, silhouette_samples

# simplest grpah
# node1 = {
#     "x" : 0,
#     "y" : 0,
#     "leiden" : 1
# }

# node2 = {
#     "x" : 1,
#     "y" : 1,
#     "leiden" : 1
# }

# node3 = {
#     "x" : 10000,
#     "y" : 10000,
#     "leiden" : 2
# }
# node4 = {
#     "x" : 0,
#     "y" : 0,
#     "leiden" : 2
# }

# data2d = [node1, node2, node3, node4]


# file dialog to open folder with graph-coordinates
root = tk.Tk()
root.withdraw()
filepath = filedialog.askdirectory()

# open graph-coordinates
with open(filepath + "/pos2d.json", "r") as f:
    data2d = json.load(f)
with open(filepath + "/pos3d.json", "r") as f:
    data3d = json.load(f)

# filter nodes without clustering and read out features and labels
# 2D
final2d = [item for item in data2d if item["leiden"] is not None]
features2d = np.array([[item["x"], item["y"]] for item in final2d]) 
labels2d = np.array([item["leiden"] for item in final2d])

# 3D
final3d = [item for item in data3d if item["leiden"] is not None]
features3d = np.array([[item["x"], item["y"], item["z"]] for item in final3d]) 
labels3d = np.array([item["leiden"] for item in final3d])

# calculate mean silhouttescores and silhouttescores for all samples
# 2D euclidean
score2d = silhouette_score(features2d, labels2d, metric="euclidean")
samples2d = silhouette_samples(features2d, labels2d, metric="euclidean")

# 3D euclidean
score3d = silhouette_score(features3d, labels3d, metric="euclidean")
samples3d = silhouette_samples(features3d, labels3d, metric="euclidean")

# 2D cosine similarity
score2dcosine = silhouette_score(features2d, labels2d, metric="cosine")
samples2dcosine = silhouette_samples(features2d, labels2d, metric="cosine")

# 3D cosine similarity
score3dcosine = silhouette_score(features3d, labels3d, metric="cosine")
samples3dcosine = silhouette_samples(features3d, labels3d, metric="cosine")

# print results
print("score2d euclidean:", score2d)
# print("samples2d euclidean:",samples2d)
print("score3d euclidean:", score3d)
# print("samples3d euclidean:",samples3d)

print("score2d cosine:", score2dcosine)
# print("samples2d cosine:",samples2dcosine)
print("score3d cosine:", score3dcosine)
# print("samples3d cosine:",samples3dcosine)