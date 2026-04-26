"""The canonical LENS perception model: logit(q_hat) = logit(q) + beta^T x + epsilon.

This is the formal object Paper 1 introduces and Papers 2 and 3 inherit. Imported
by simulation code and calibration code so the formula lives in exactly one place.
"""

from __future__ import annotations

import numpy as np
from scipy.special import expit, logit


def perceived_logit(
    q: np.ndarray | float,
    x: np.ndarray,
    beta: np.ndarray,
    epsilon: np.ndarray | float = 0.0,
) -> np.ndarray:
    """Perception in log-odds space.

    Args:
        q:       true quality / success probability in (0, 1). Scalar or shape (n,).
        x:       observable features. Shape (n, d) or (d,) for a single candidate.
        beta:    bias vector. Shape (d,).
        epsilon: random noise term. Scalar or shape (n,).

    Returns:
        log-odds of perceived quality. Same shape as q.
    """
    x = np.atleast_2d(x)
    return logit(np.asarray(q)) + x @ beta + epsilon


def perceived_probability(
    q: np.ndarray | float,
    x: np.ndarray,
    beta: np.ndarray,
    epsilon: np.ndarray | float = 0.0,
) -> np.ndarray:
    """Perceived quality back on the probability scale (inverse logit applied)."""
    return expit(perceived_logit(q, x, beta, epsilon))


def winner_curse_expected_error(sigma_epsilon: float, n: int) -> float:
    """Paper 1: E[epsilon_winner] ~= sigma_epsilon * sqrt(log N)."""
    if n <= 1:
        return 0.0
    return sigma_epsilon * float(np.sqrt(np.log(n)))


def committee_bias_variance(
    sigma_beta_sq: float,
    rho_beta: float,
    k: int,
) -> float:
    """Paper 1 / Paper 2: Var(beta_bar) = sigma_beta^2 * [rho + (1 - rho)/k]."""
    if k <= 0:
        raise ValueError("committee size must be positive")
    return sigma_beta_sq * (rho_beta + (1.0 - rho_beta) / k)
