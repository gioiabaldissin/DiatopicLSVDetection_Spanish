from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.metrics import calinski_harabasz_score

def cluster_kmeans(n_clusters, vectors):
  """
  Clusters the vectors in the defined number of clusters
  :param n_clusters: number of clusters to partition the vectors
  :param vectors: vectors to cluster
  :return a model with the fit vectors:
  """
  km = KMeans(n_clusters=n_clusters)
  km.fit(vectors)
  #labels = km.labels_

  return km

def select_best_kmeans(vectors, metric='silhouette'):
  """
  Select the K-Mean model that best fit the vectors. 
  Inspect number of clusters between 2 and 8 and compute the score based on the paramter metric to determine which number is best.
  Supported metrics only work in a range(2, len(vectors)), hence the minimum number of clusters is 2. 
  Max is 8 since it is unlikely, that a word has so many senses, i.e. clusters.
  :param vectors: vectors to cluster
  :param metric: metric to decide which model is best. Supported are silhouette and calinski. Silhouette is the default.
  :return The best model for the vectors:
  """
  min_n_cluster = 2
  max_n_cluster = 8

  best_model = None
  best_score = -1

  for n_clusters in range(min_n_cluster, max_n_cluster + 1):
    model = cluster_kmeans(n_clusters, vectors)

    if metric == 'silhouette':
      current_score = silhouette_score(vectors, model.labels_)
    elif metric == "calinski":
      current_score = calinski_harabasz_score(vectors, model.labels_)
    else:
      raise Exception("Invalid metric: " + metric)
    
    if current_score > best_score:
      best_score = current_score
      best_model = model

  return best_model