"""Diversity filter for similar-image deduplication.

Clusters generated images by visual similarity (K-Means on downscaled
pixel features) and selects the highest-scored representative from each
cluster. Ensures the human-review set contains diverse candidates
rather than near-duplicates (D-04).

Usage:
    filter = DiversityFilter(n_clusters=5)
    selected = filter.cluster_and_select(images, scores, n_select=5)
    # Returns [(index, score), ...] sorted by score descending
"""

import warnings
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image


class DiversityFilter:
    """Cluster-based diversity selection for image candidates.

    Groups similar images and picks the best-scored representative
    from each group to ensure visual diversity in the selected set.
    """

    def __init__(self, n_clusters: int = 5, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state

    def _image_to_feature(self, image: Image.Image) -> np.ndarray:
        """Convert a PIL Image to a flattened 64x64 RGB feature vector.

        Args:
            image: Input PIL Image (any size).

        Returns:
            1D numpy array of shape (64*64*3,) = (12288,).
        """
        resized = image.convert("RGB").resize((64, 64), Image.LANCZOS)
        arr = np.array(resized).astype(np.float32)
        return arr.flatten()

    def cluster_and_select(
        self,
        images: List[Image.Image],
        scores: List[float],
        n_select: int = 5,
    ) -> List[Tuple[int, float]]:
        """Cluster images and select a diverse subset.

        Args:
            images: List of PIL Images to cluster.
            scores: Parallel list of scores (0.0-1.0) for each image.
            n_select: Maximum number of diverse images to return.

        Returns:
            List of (index, score) tuples for the selected subset,
            sorted by score descending. Empty list if input is empty.
        """
        if not images or not scores:
            return []

        # Validate lengths match
        if len(images) != len(scores):
            raise ValueError(
                f"images ({len(images)}) and scores ({len(scores)}) "
                f"must have the same length"
            )

        n_images = len(images)
        effective_clusters = min(self.n_clusters, n_images)

        # If only one cluster needed, return top-N by score
        if effective_clusters <= 1:
            sorted_indices = sorted(
                range(n_images), key=lambda i: scores[i], reverse=True
            )
            return [(i, scores[i]) for i in sorted_indices[:n_select]]

        # Build feature matrix
        features = np.array([self._image_to_feature(img) for img in images])

        try:
            from sklearn.cluster import MiniBatchKMeans

            kmeans = MiniBatchKMeans(
                n_clusters=effective_clusters,
                random_state=self.random_state,
                n_init="auto",
            )
            labels = kmeans.fit_predict(features)
        except ImportError as exc:
            warnings.warn(
                f"sklearn.cluster.MiniBatchKMeans not available ({exc}). "
                f"Falling back to score-based selection."
            )
            sorted_indices = sorted(
                range(n_images), key=lambda i: scores[i], reverse=True
            )
            return [(i, scores[i]) for i in sorted_indices[:n_select]]
        except Exception as exc:
            warnings.warn(
                f"Clustering failed: {exc}. "
                f"Falling back to score-based selection."
            )
            sorted_indices = sorted(
                range(n_images), key=lambda i: scores[i], reverse=True
            )
            return [(i, scores[i]) for i in sorted_indices[:n_select]]

        # For each cluster, select the highest-scored image
        cluster_best: dict[int, Tuple[int, float]] = {}
        for idx in range(n_images):
            label = int(labels[idx])
            score = scores[idx]
            if label not in cluster_best or score > cluster_best[label][1]:
                cluster_best[label] = (idx, score)

        # Sort by score descending and limit to n_select
        selected = sorted(
            cluster_best.values(), key=lambda x: x[1], reverse=True
        )
        return selected[:n_select]
