from sklearn.mixture import GaussianMixture as GMM
import numpy as np

def get_best_gmm(vectors_train):
  """
  Uses BIC to infer the best GMM that fits the vectors
  :param vectors_train: vectors to cluster
  :return the model that best fit the vectors:
  """
  X = np.array(vectors_train)

  lowest_bic = np.infty
  bic_list = []
  n_components_range = range(1, 9)
  cv_types = ['spherical', 'tied', 'diag', 'full']
  for cv_type in cv_types:
      for n_components in n_components_range:
          # Fit a Gaussian mixture with EM
          gmm = GMM(n_components=n_components,covariance_type=cv_type)
          gmm.fit(X)
          bic_list.append(gmm.bic(X))
          if bic_list[-1] < lowest_bic:
              lowest_bic = bic_list[-1]
              best_gmm = gmm
  return best_gmm