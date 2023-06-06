import json
import numpy as np
from sklearn.metrics import silhouette_score

with open("trump2D.json", "r") as f:
    data2d = json.load(f)

with open("trump3D.json", "r") as f:
    data3d = json.load(f)

#print(data2d[0]["screen_name"])
#print(data3d[0]["screen_name"])


final2d = [item for item in data2d if item["leiden"] is not None]


features2d = np.array([[item["x"], item["y"]] for item in final2d]) 
labels2d = np.array([item["leiden"] for item in final2d])

#print(len(features2d), features2d)
#print(len(labels2d), labels2d)

score2d = silhouette_score(features2d, labels2d, metric="euclidean")
print("score2d:",score2d)


final3d = [item for item in data3d if item["leiden"] is not None]

features3d = np.array([[item["x"], item["y"], item["z"]] for item in final3d]) 
labels3d = np.array([item["leiden"] for item in final3d])

#print(len(features3d), features3d)
#print(len(labels3d), labels3d)

score3d = silhouette_score(features3d, labels3d, metric="euclidean")
print("score3d:", score3d)
