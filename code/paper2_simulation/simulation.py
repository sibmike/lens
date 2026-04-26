"""
PRISM: Progressive Refinement in Selection Modeling
Production Implementation

A framework for simulating multi-stage human decision processes, particularly
focused on venture capital investment selection. The framework models how
different evaluators (with their own biases) perceive candidate quality
through noisy signals, and how different selection architectures (sequential
vs batch, individual vs committee) affect outcomes.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Iterator, Tuple, Union, Any
from abc import ABC, abstractmethod
from scipy.special import logit, expit
import json
from tqdm import tqdm



# Standard investor archetypes based on real-world data
INVESTOR_CONFIGS = {
    'angel_investor': {
        'name': 'Angel Investor',
        'review_count': 120,
        'stages': [{
            'name': 'Sequential Review',
            'batcher': {'type': 'stream'},  # Reviews deals one by one
            'evaluators': {
                'pool_size': 1,
                'committee_size': 1,
                'pool_prefix': 'angel',
                'sampling': 'identity',
                'aggregation': 'mean'
            },
            'selector': {
                'type': 'threshold',
                'threshold': 0.01  # 1% minimum success probability
            },
            'max_output': 12  # Target portfolio size
        }]
    },
    
    'angel_group': {
        'name': 'Angel Group',
        'review_count': 600,
        'stages': [
            {
                'name': 'Individual Sourcing',
                'batcher': {'type': 'stream'},  # Each angel sources individually
                'evaluators': {
                    'pool_size': 5,  # 5 angels in the group
                    'committee_size': 1,  # Each sources individually
                    'pool_prefix': 'angel',
                    'sampling': 'random',  # Different angel for each startup
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'threshold',
                    'threshold': 0.01  # Same threshold as individual angel
                },
                'max_output': 60  # 5 angels × 12 each = 60 sourced deals
            },
            {
                'name': 'Committee Review',
                'batcher': {'type': 'full'},  # All sourced deals reviewed together
                'evaluators': {
                    'pool_size': 5,  # Same 5 angels now as committee
                    'committee_size': 5,
                    'pool_prefix': 'angel',
                    'sampling': 'identity',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 20.0  # Select top 20% (12 from 60)
                }
            }
        ]
    },
    
    'yc': {
        'name': 'Y Combinator',
        'review_count': 10000,
        'stages': [
            {
                'name': 'Application Review',
                'batcher': {'type': 'full'},  # Single batch review
                'evaluators': {
                    'pool_size': 50,  # Large pool of alumni reviewers
                    'committee_size': 2,  # Each app gets 2 reviewers
                    'pool_prefix': 'reviewer',
                    'sampling': 'random',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 6.0  # ~5% get interviews from 10k
                }
            },
            {
                'name': 'Partner Interview',
                'batcher': {'type': 'stream'},  # Individual 10-min interviews
                'evaluators': {
                    'pool_size': 19,  # 19 group partners
                    'committee_size': 3,  # 3 partners per interview
                    'pool_prefix': 'partner',
                    'sampling': 'random',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 30.0  # ~1.8% overall)
                }
            }
        ]
    },
    
    'seed_fund': {
        'name': 'Seed Fund',
        'review_count': 500,
        'stages': [{
            'name': 'Partner Review',
            'batcher': {'type': 'stream'},  # Rolling basis
            'evaluators': {
                'pool_size': 3,  # Small partnership
                'committee_size': 3,
                'pool_prefix': 'partner',
                'sampling': 'identity',
                'aggregation': 'mean'
            },
            'selector': {
                'type': 'threshold',
                'threshold': 0.008  # Lower bar for seed stage
            },
            'max_output': 40  # High volume strategy
        }]
    },
    
    'general_vc': {
        'name': 'General VC Fund',
        'review_count': 1200,
        'stages': [
            {
                'name': 'Associate Screen',
                'batcher': {'type': 'chunk', 'chunk_size': 100},  # Weekly batches
                'evaluators': {
                    'pool_size': 2,  # 2 associates
                    'committee_size': 1,  # Each reviews independently
                    'pool_prefix': 'associate',
                    'sampling': 'random',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 8.0  # 8% get partner meeting
                }
            },
            {
                'name': 'Partner Meeting',
                'batcher': {'type': 'full'},  # All partners review shortlist
                'evaluators': {
                    'pool_size': 5,  # 4-6 partners typical
                    'committee_size': 5,
                    'pool_prefix': 'partner',
                    'sampling': 'identity',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'top_k',
                    'k': 4  # 4 investments annually (0.33% overall)
                }
            }
        ]
    },
    
    'elite_vc': {
        'name': 'Elite VC Fund',
        'review_count': 5000,
        'stages': [
            {
                'name': 'Analyst Screen',
                'batcher': {'type': 'chunk', 'chunk_size': 1000},  # Large batches
                'evaluators': {
                    'pool_size': 8,  # More analysts for larger funnel
                    'committee_size': 2,  # Each deal gets 2 reviewers
                    'pool_prefix': 'analyst',
                    'sampling': 'random',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 2.0  # 200 advance from 10000 (wider funnel)
                }
            },
            {
                'name': 'Partnership Review',
                'batcher': {'type': 'full'},
                'evaluators': {
                    'pool_size': 12,  # Large partnership
                    'committee_size': 12,
                    'pool_prefix': 'partner',
                    'sampling': 'identity',
                    'aggregation': 'median'  # More conservative
                },
                'selector': {
                    'type': 'top_k',
                    'k': 20  # 20 investments (0.2% overall)
                }
            }
        ]
    },
    
    'cyrannus': {
        'name': 'Cyrannus Platform',
        'review_count': 4000,
        'stages': [
            {
                'name': 'Scout Discovery',
                'batcher': {
                    'type': 'chunk',
                    'chunk_size': 200  # Each scout sees 200 startups
                },
                'evaluators': {
                    'pool_size': 10,  # 10 diverse scouts
                    'committee_size': 1,  # Individual evaluation
                    'pool_prefix': 'scout',
                    'sampling': 'random',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'threshold',
                    'threshold': 0.008  # Lower bar for seed stage
                },
            },
            {
                'name': 'Expert Committee 1',
                'batcher': {'type': 'full'},
                'evaluators': {
                    'pool_size': 10,  # First expert committee
                    'committee_size': 10,
                    'pool_prefix': 'expert1',
                    'sampling': 'identity',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 50.0  # 500 advance from 1000
                }
            },
            {
                'name': 'Expert Committee 2',
                'batcher': {'type': 'full'},
                'evaluators': {
                    'pool_size': 20,  # Larger final committee
                    'committee_size': 20,
                    'pool_prefix': 'expert2',
                    'sampling': 'identity',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'top_k',
                    'k': 100  # Fund 100 companies (5% overall)
                }
            }
        ]
    },
    # Special variant for Cyrannus with AI model (when use_pitch_filter=True)
    'cyrannus_ai_noscout': {
        'name': 'Cyrannus Platform (AI-Enhanced) - No Scouts',
        'review_count': 4000,
        'stages': [
            {
                'name': 'AI Model Filter',
                'batcher': {'type': 'full'},
                'evaluators': {
                    'pool_size': 1,
                    'committee_size': 1,
                    'pool_prefix': 'ai_model',
                    'sampling': 'identity',
                    'aggregation': 'mean',
                    'bias_overrides': {
                        'pitch_sensitivity': 0.0,  # AI is unbiased
                        'profile_bias': 0.0,
                        'noise_std': 0.3  # Lower noise than humans
                    }
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 50.0  # 500 from 1000
                }
            },
            {
                'name': 'Expert Committee 1',
                'batcher': {'type': 'full'},
                'evaluators': {
                    'pool_size': 10,
                    'committee_size': 10,
                    'pool_prefix': 'expert1',
                    'sampling': 'identity',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 20.0  # 200 from 500
                }
            },
            {
                'name': 'Expert Committee 2',
                'batcher': {'type': 'full'},
                'evaluators': {
                    'pool_size': 20,
                    'committee_size': 20,
                    'pool_prefix': 'expert2',
                    'sampling': 'identity',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 25.0  # 100 from 200 (5% overall)
                }
            }
        ]
    },
    # Special variant for Cyrannus with AI model (when use_pitch_filter=True)
    'cyrannus_ai_20': {
        'name': 'Cyrannus Platform (AI-Enhanced) - 20 DD experts',
        'review_count': 10000,
        'stages': [
            {
                'name': 'Scout Discovery',
                'batcher': {
                    'type': 'chunk',
                    'chunk_size': 200
                },
                'evaluators': {
                    'pool_size': 10,
                    'committee_size': 1,
                    'pool_prefix': 'scout',
                    'sampling': 'random',
                    'aggregation': 'mean'
                },
                 'selector': {
                    'type': 'threshold',
                    'threshold': 0.008  # Lower bar for seed stage
                },
            },
            {
                'name': 'AI Model Filter',
                'batcher': {'type': 'full'},
                'evaluators': {
                    'pool_size': 1,
                    'committee_size': 1,
                    'pool_prefix': 'ai_model',
                    'sampling': 'identity',
                    'aggregation': 'mean',
                    'bias_overrides': {
                        'pitch_sensitivity': 0.0,  # AI is unbiased
                        'profile_bias': 0.0,
                        'noise_std': 0.3  # Lower noise than humans
                    }
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 50.0  # 500 from 1000
                }
            },
            {
                'name': 'Expert Committee 1',
                'batcher': {'type': 'full'},
                'evaluators': {
                    'pool_size': 10,
                    'committee_size': 10,
                    'pool_prefix': 'expert1',
                    'sampling': 'identity',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 20.0  # 200 from 500
                }
            },
            {
                'name': 'Expert Committee 2',
                'batcher': {'type': 'full'},
                'evaluators': {
                    'pool_size': 20,
                    'committee_size': 20,
                    'pool_prefix': 'expert2',
                    'sampling': 'identity',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 50.0  # 100 from 200 (5% overall)
                }
            }
        ]
    },
    # Special variant for Cyrannus with AI model (when use_pitch_filter=True)
    'cyrannus_ai_10': {
        'name': 'Cyrannus Platform (AI-Enhanced) - 10 DD experts',
        'review_count': 10000,
        'stages': [
            {
                'name': 'Scout Discovery',
                'batcher': {
                    'type': 'chunk',
                    'chunk_size': 200
                },
                'evaluators': {
                    'pool_size': 10,
                    'committee_size': 1,
                    'pool_prefix': 'scout',
                    'sampling': 'random',
                    'aggregation': 'mean'
                },
                 'selector': {
                    'type': 'threshold',
                    'threshold': 0.008  # Lower bar for seed stage
                },
            },
            {
                'name': 'AI Model Filter',
                'batcher': {'type': 'full'},
                'evaluators': {
                    'pool_size': 1,
                    'committee_size': 1,
                    'pool_prefix': 'ai_model',
                    'sampling': 'identity',
                    'aggregation': 'mean',
                    'bias_overrides': {
                        'pitch_sensitivity': 0.0,  # AI is unbiased
                        'profile_bias': 0.0,
                        'noise_std': 0.3  # Lower noise than humans
                    }
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 50.0  # 500 from 1000
                }
            },
            {
                'name': 'Expert Committee 1',
                'batcher': {'type': 'full'},
                'evaluators': {
                    'pool_size': 10,
                    'committee_size': 10,
                    'pool_prefix': 'expert1',
                    'sampling': 'identity',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 20.0  # 200 from 500
                }
            },
            {
                'name': 'Expert Committee 2',
                'batcher': {'type': 'full'},
                'evaluators': {
                    'pool_size': 20,
                    'committee_size': 10,
                    'pool_prefix': 'expert2',
                    'sampling': 'identity',
                    'aggregation': 'mean'
                },
                'selector': {
                    'type': 'top_percent',
                    'percent': 50.0  # 100 from 200 (5% overall)
                }
            }
        ]
    },
    'cyrannus_ai_angel': {
    'name': 'Angel via Cyrannus Platform (AI-Enhanced)',
    'review_count': 10000,
    'stages': [
        # First, run the Cyrannus AI selection process
        {
            'name': 'Scout Discovery',
            'batcher': {
                'type': 'chunk',
                'chunk_size': 200
            },
            'evaluators': {
                'pool_size': 10,
                'committee_size': 1,
                'pool_prefix': 'scout',
                'sampling': 'random',
                'aggregation': 'mean'
            },
            'selector': {
                'type': 'threshold',
                'threshold': 0.008  # Lower bar for seed stage
            },
        },
        {
            'name': 'AI Model Filter',
            'batcher': {'type': 'full'},
            'evaluators': {
                'pool_size': 1,
                'committee_size': 1,
                'pool_prefix': 'ai_model',
                'sampling': 'identity',
                'aggregation': 'mean',
                'bias_overrides': {
                    'pitch_sensitivity': 0.0,  # AI is unbiased
                    'profile_bias': 0.0,
                    'noise_std': 0.3  # Lower noise than humans
                }
            },
            'selector': {
                'type': 'top_percent',
                'percent': 50.0  # 500 from 1000
            }
        },
        {
            'name': 'Expert Committee 1',
            'batcher': {'type': 'full'},
            'evaluators': {
                'pool_size': 10,
                'committee_size': 10,
                'pool_prefix': 'expert1',
                'sampling': 'identity',
                'aggregation': 'mean'
            },
            'selector': {
                'type': 'top_percent',
                'percent': 20.0  # 200 from 500
            }
        },
        {
            'name': 'Expert Committee 2',
            'batcher': {'type': 'full'},
            'evaluators': {
                'pool_size': 20,
                'committee_size': 10,
                'pool_prefix': 'expert2',
                'sampling': 'identity',
                'aggregation': 'mean'
            },
            'selector': {
                'type': 'top_percent',
                'percent': 50.0  # 100 from 2000 (5% overall)
            }
        },
        # Individual angel reviews the 100 pre-filtered startups
        {
            'name': 'Angel Individual Selection',
            'batcher': {'type': 'full'},  # Reviews all 100 in batch
            'evaluators': {
                'pool_size': 1,  # Single angel investor
                'committee_size': 1,
                'pool_prefix': 'angel',
                'sampling': 'identity',
                'aggregation': 'mean'
            },
            'selector': {
                'type': 'top_percent',
                'percent': 20.0  # Selects top 20% (20 from 100)
            }
        }
    ]}
}
# ==================== Data Structures ====================

@dataclass
class CandidateBatch:
    """
    Represents a batch of candidates (e.g., startups) with their true qualities
    and observable features. Uses numpy arrays for efficient vectorized operations.
    
    Hidden from evaluators:
    - true_probabilities: The actual success probability
    - is_unicorn: Whether this startup will actually become a unicorn
    
    Observable by evaluators (with bias):
    - pitch_qualities: Communication effectiveness
    - has_perfect_profile: Elite background signals
    """
    ids: np.ndarray                    # Unique identifier for each candidate
    true_probabilities: np.ndarray     # True success probability (hidden from evaluators)
    pitch_qualities: np.ndarray        # How well the opportunity is communicated (-∞ to +∞)
    has_perfect_profile: np.ndarray    # Binary: elite background (Stanford/MIT + ex-FAANG, etc.)
    is_unicorn: np.ndarray             # Binary: actual outcome (becomes unicorn or not)
    is_funded: np.ndarray = None       # Tracking: whether candidate was funded
    features: Dict[str, np.ndarray] = field(default_factory=dict)  # Extensible features
    
    def __len__(self):
        return len(self.ids)
    
    def subset(self, indices: np.ndarray) -> 'CandidateBatch':
        """Create a subset of candidates maintaining all attributes."""
        return CandidateBatch(
            ids=self.ids[indices],
            true_probabilities=self.true_probabilities[indices],
            pitch_qualities=self.pitch_qualities[indices],
            has_perfect_profile=self.has_perfect_profile[indices],
            is_unicorn=self.is_unicorn[indices],
            is_funded=self.is_funded[indices] if self.is_funded is not None else None,
            features={k: v[indices] for k, v in self.features.items()}
        )
    
    @staticmethod
    def generate(n: int = 30000, seed: int = 42) -> 'CandidateBatch':
        """
        Generate a realistic population of startups with calibrated quality distribution.
        
        The distribution is designed so that the top ~17% (5000 of 30000) average
        1.677% success probability, matching empirical data that ~1% of funded
        startups become unicorns.
        """
        np.random.seed(seed)
        
        # Quality tiers based on empirical startup data
        buckets = {
            'very_low': (0.0001, 0.0006),   # 0.01% to 0.06% success probability
            'low': (0.0006, 0.006),          # 0.06% to 0.6%
            'medium': (0.006, 0.035),        # 0.6% to 3.5%
            'high': (0.035, 0.09)            # 3.5% to 9%
        }
        
        # Distribution across tiers (calibrated to match real startup ecosystem)
        bucket_percentages = {
            'very_low': 0.60,   # 60% are very low quality
            'low': 0.30,        # 30% are low quality
            'medium': 0.09,     # 9% are medium quality
            'high': 0.01        # 1% are high quality (potential unicorns)
        }
        
        # Generate success probabilities
        all_probs = []
        for bucket, percentage in bucket_percentages.items():
            n_in_bucket = int(percentage * n)
            min_prob, max_prob = buckets[bucket]
            bucket_probs = np.random.uniform(min_prob, max_prob, n_in_bucket)
            all_probs.extend(bucket_probs)
        
        # Handle rounding
        while len(all_probs) < n:
            all_probs.append(np.random.uniform(0.0001, 0.001))
        
        true_probabilities = np.array(all_probs[:n])
        np.random.shuffle(true_probabilities)
        
        # Generate observable features
        # Pitch quality: N(0, 2) - high variance in communication skills
        pitch_qualities = np.random.normal(0, 2, n)
        
        # Perfect profile: ~5% have the narrow combination that triggers investor bias
        has_perfect_profile = np.random.random(n) < 0.05
        
        # Determine actual outcomes based on true probabilities
        # Each startup's fate is determined at creation: random draw < probability = unicorn
        is_unicorn = np.random.random(n) < true_probabilities
        
        return CandidateBatch(
            ids=np.arange(n),
            true_probabilities=true_probabilities,
            pitch_qualities=pitch_qualities,
            has_perfect_profile=has_perfect_profile.astype(bool),
            is_unicorn=is_unicorn.astype(bool),
            is_funded=np.zeros(n, dtype=bool)
        )


@dataclass
class StageResult:
    """Results from processing candidates through a single stage of the pipeline."""
    stage_name: str
    input_count: int
    output_count: int
    selected_indices: np.ndarray      # Which candidates were selected
    scores: np.ndarray                # Evaluation scores for all candidates
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Complete results from running candidates through an entire pipeline."""
    pipeline_name: str
    final_selection: CandidateBatch
    stage_results: List[StageResult]
    summary_metrics: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate summary metrics after pipeline execution."""
        if len(self.final_selection) > 0:
            self.summary_metrics.update({
                'portfolio_size': len(self.final_selection),
                'avg_true_probability': self.final_selection.true_probabilities.mean(),
                'avg_pitch_quality': self.final_selection.pitch_qualities.mean(),
                'pct_perfect_profile': self.final_selection.has_perfect_profile.mean(),
                'total_evaluated': self.stage_results[0].input_count if self.stage_results else 0,
                'acceptance_rate': len(self.final_selection) / self.stage_results[0].input_count if self.stage_results else 0,
                # Expected value: sum of probabilities (e.g., 5 startups × 2% each = 0.1 expected)
                'expected_successes': self.final_selection.true_probabilities.sum(),
                # Actual outcomes: count of startups that became unicorns (0, 1, 2, etc.)
                'actual_unicorns': self.final_selection.is_unicorn.sum(),
                # Probability of at least one success in portfolio
                'portfolio_success_prob': 1 - np.prod(1 - self.final_selection.true_probabilities),
            })


# ==================== Core Components ====================

@dataclass
class BiasProfile:
    """
    Represents an individual evaluator's perception model, including their
    systematic biases and random noise. Each evaluator sees candidate quality
    through their own biased lens.
    """
    id: str
    pitch_sensitivity: float      # β_pitch: How much pitch quality affects perception [0.3-1.2]
    profile_bias: float          # β_profile: Bias toward "perfect" profiles (can be negative)
    noise_std: float            # σ: Random evaluation noise (typically 0.5)
    domain_expertise: Dict[str, float] = field(default_factory=dict)  # For future extensions
    time_availability: float = 1.0
    
    @staticmethod
    def generate_random(id: str, seed: Optional[int] = None) -> 'BiasProfile':
        """
        Generate a random evaluator with realistic bias parameters.
        Based on empirical studies of investor behavior.
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Most investors try to see past pitch quality but can't fully (mean=0.75)
        pitch_sensitivity = np.clip(np.random.normal(0.75, 0.15), 0.3, 1.2)
        
        # 30% of investors are unbiased, 70% show profile bias (mostly positive)
        if np.random.random() < 0.3:
            profile_bias = 0.0
        else:
            profile_bias = np.random.normal(0.5, 0.3)
            
        return BiasProfile(
            id=id,
            pitch_sensitivity=pitch_sensitivity,
            profile_bias=profile_bias,
            noise_std=0.5  # Standard noise level
        )
    
    def perceive(self, 
                 true_probabilities: np.ndarray,
                 pitch_qualities: np.ndarray,
                 has_perfect_profile: np.ndarray,
                 seed: Optional[int] = None) -> np.ndarray:
        """
        Calculate perceived quality for each candidate based on true quality plus biases.
        
        Note: Evaluators cannot see the actual outcome (is_unicorn), only the signals.
        
        The perception model in log-odds space:
        logit(perceived) = logit(true) + β_pitch*pitch + β_profile*profile + noise
        
        This ensures realistic behavior where:
        - Good pitch can make 0.5% startup look like 2% (4x multiplier)
        - But can only make 0.1% startup look like 0.4% (still unfundable)
        - Effects are multiplicative, not additive
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Work in log-odds space to ensure proper probability bounds
        p_clipped = np.clip(true_probabilities, 1e-10, 1 - 1e-10)
        true_log_odds = logit(p_clipped)
        
        # Add systematic biases
        pitch_effect = self.pitch_sensitivity * pitch_qualities
        profile_effect = self.profile_bias * has_perfect_profile.astype(float)
        
        # Add random perception noise
        noise = np.random.normal(0, self.noise_std, len(true_probabilities))
        
        # Combine all effects in log-odds space
        perceived_log_odds = true_log_odds + pitch_effect + profile_effect + noise
        
        # Convert back to probability space
        perceived_probs = expit(perceived_log_odds)
        
        return np.clip(perceived_probs, 0, 1)


# ==================== Evaluators ====================

@dataclass
class Evaluators:
    """
    Manages a group of evaluators (committee or individual) and how they
    collectively evaluate candidates. Handles both single evaluators and
    multi-person committees with various voting rules.
    """
    pool: List[BiasProfile]           # All available evaluators
    committee_size: int               # How many evaluate each batch
    sampling: str = 'identity'        # 'identity' or 'random'
    aggregation: str = 'mean'         # 'mean' or 'median'
    
    def evaluate(self, candidates: CandidateBatch, context_id: int = 0, seed: Optional[int] = None) -> np.ndarray:
        """
        Evaluate all candidates and return aggregated scores.
        
        Process:
        1. Select committee members from pool
        2. Each member evaluates all candidates independently
        3. Aggregate scores across committee members
        """
        # Select evaluators for this batch
        if self.sampling == 'identity' or self.committee_size >= len(self.pool):
            committee = self.pool[:self.committee_size]
        else:  # random sampling
            np.random.seed((context_id * 1000) % 2**32)
            indices = np.random.choice(len(self.pool), size=self.committee_size, replace=False)
            committee = [self.pool[i] for i in indices]
        
        # Each evaluator scores all candidates
        scores = []
        for i, evaluator in enumerate(committee):
            # Ensure independent random noise for each evaluator
            eval_seed = None if seed is None else seed + i + context_id * 1000
            evaluator_scores = evaluator.perceive(
                candidates.true_probabilities,
                candidates.pitch_qualities,
                candidates.has_perfect_profile,
                seed=eval_seed
            )
            scores.append(evaluator_scores)
        
        # Stack into matrix: rows = evaluators, columns = candidates
        scores_matrix = np.vstack(scores)
        
        # Aggregate across evaluators
        if self.aggregation == 'mean':
            return scores_matrix.mean(axis=0)
        elif self.aggregation == 'median':
            return np.median(scores_matrix, axis=0)
        else:
            raise ValueError(f"Unknown aggregation method: {self.aggregation}")


# ==================== Batching ====================

class Batcher(ABC):
    """Determines how candidates are grouped for evaluation."""
    
    @abstractmethod
    def get_batches(self, candidates: CandidateBatch) -> Iterator[Tuple[CandidateBatch, np.ndarray]]:
        """Yield batches of candidates with their original indices."""
        pass


class FullBatcher(Batcher):
    """Process all candidates as one batch (enables relative comparison)."""
    
    def get_batches(self, candidates: CandidateBatch) -> Iterator[Tuple[CandidateBatch, np.ndarray]]:
        indices = np.arange(len(candidates))
        yield candidates, indices


class ChunkBatcher(Batcher):
    """Process candidates in fixed-size chunks (e.g., weekly batches)."""
    
    def __init__(self, chunk_size: int):
        self.chunk_size = chunk_size
    
    def get_batches(self, candidates: CandidateBatch) -> Iterator[Tuple[CandidateBatch, np.ndarray]]:
        n = len(candidates)
        for i in range(0, n, self.chunk_size):
            indices = np.arange(i, min(i + self.chunk_size, n))
            yield candidates.subset(indices), indices


class StreamBatcher(Batcher):
    """Process candidates one at a time (sequential evaluation)."""
    
    def get_batches(self, candidates: CandidateBatch) -> Iterator[Tuple[CandidateBatch, np.ndarray]]:
        for i in range(len(candidates)):
            indices = np.array([i])
            yield candidates.subset(indices), indices


# ==================== Selection ====================

class Selector:
    """
    Selects candidates based on scores using various criteria.
    All selection methods follow the same pattern: compute threshold, select above it.
    """
    
    def __init__(self, criterion_type: str, value: float = None):
        """
        Initialize selector with criterion type and value.
        
        Args:
            criterion_type: 'threshold', 'top_k', or 'top_percent'
            value: threshold value, k candidates, or percentage
        """
        self.criterion_type = criterion_type
        self.value = value
    
    def select(self, scores: np.ndarray, batch_indices: np.ndarray, max_selections: Optional[int] = None) -> np.ndarray:
        """
        Select candidates based on criterion, with optional maximum limit.
        Returns indices into the original candidate array.
        """
        # Compute threshold based on criterion
        if self.criterion_type == 'threshold':
            threshold = self.value
        elif self.criterion_type == 'top_k':
            if len(scores) <= self.value:
                threshold = -np.inf
            else:
                # Use partition for efficiency instead of full sort
                k = int(self.value)
                threshold = np.partition(scores, -k)[-k]
        elif self.criterion_type == 'top_percent':
            if len(scores) == 0:
                threshold = np.inf
            else:
                percentile = 100 - self.value
                threshold = np.percentile(scores, percentile)
        else:
            raise ValueError(f"Unknown criterion type: {self.criterion_type}")
        
        # Select indices above threshold
        selected_batch_indices = np.where(scores >= threshold)[0]
        
        # Handle top_k edge case where multiple candidates have the threshold score
        if self.criterion_type == 'top_k' and len(selected_batch_indices) > self.value:
            # Sort by score and take exactly k
            sorted_indices = selected_batch_indices[np.argsort(scores[selected_batch_indices])[::-1]]
            selected_batch_indices = sorted_indices[:int(self.value)]
        
        # Apply maximum selection limit if specified
        if max_selections is not None and len(selected_batch_indices) > max_selections:
            sorted_indices = selected_batch_indices[np.argsort(scores[selected_batch_indices])[::-1]]
            selected_batch_indices = sorted_indices[:max_selections]
        
        # Convert to original indices
        return batch_indices[selected_batch_indices]


# ==================== Stage & Pipeline ====================

@dataclass
class Stage:
    """
    A single stage in the selection pipeline, combining batching, evaluation,
    and selection. Examples: resume screening, phone interviews, final round.
    """
    name: str
    batcher: Batcher
    evaluators: Evaluators
    selector: Selector
    min_output: Optional[int] = None  # Minimum candidates to advance
    max_output: Optional[int] = None  # Maximum candidates to advance (portfolio limit)
    
    def process(self, candidates: CandidateBatch, stage_id: int = 0, seed: Optional[int] = None) -> StageResult:
        """Process all candidates through this stage."""
        input_count = len(candidates)
        all_selected_indices = []
        all_scores = []
        
        remaining_selections = self.max_output
        
        # Process each batch
        batch_id = 0
        for batch, batch_indices in self.batcher.get_batches(candidates):
            # Evaluate batch
            batch_seed = None if seed is None else seed + stage_id * 10000 + batch_id * 100
            scores = self.evaluators.evaluate(batch, context_id=batch_id, seed=batch_seed)
            
            # Select from batch
            selected = self.selector.select(scores, batch_indices, remaining_selections)
            
            all_selected_indices.extend(selected)
            all_scores.extend(scores)
            
            # Update remaining selections
            if remaining_selections is not None:
                remaining_selections -= len(selected)
                if remaining_selections <= 0:
                    break
                    
            batch_id += 1
        
        selected_indices = np.array(all_selected_indices)
        scores = np.array(all_scores)
        
        return StageResult(
            stage_name=self.name,
            input_count=input_count,
            output_count=len(selected_indices),
            selected_indices=selected_indices,
            scores=scores,
            metrics={
                'acceptance_rate': len(selected_indices) / input_count if input_count > 0 else 0,
                'avg_score': scores.mean() if len(scores) > 0 else 0,
            }
        )


@dataclass
class Pipeline:
    """
    Multi-stage selection pipeline. Candidates flow through stages sequentially,
    with only selected candidates advancing to the next stage.
    """
    name: str
    stages: List[Stage]
    
    def run(self, initial_candidates: CandidateBatch, seed: Optional[int] = None) -> PipelineResult:
        """Run candidates through all stages and return results."""
        stage_results = []
        candidates = initial_candidates
        
        for i, stage in enumerate(self.stages):
            # Process stage with unique random seed
            stage_seed = None if seed is None else seed + i * 100000
            result = stage.process(candidates, stage_id=i, seed=stage_seed)
            stage_results.append(result)
            
            # Check if any candidates remain
            if result.output_count == 0:
                break
            
            # Prepare candidates for next stage
            candidates = candidates.subset(result.selected_indices)
        
        return PipelineResult(
            pipeline_name=self.name,
            final_selection=candidates,
            stage_results=stage_results
        )


# ==================== Factory System ====================

def create_pipeline_from_config(config: Dict[str, Any]) -> Pipeline:
    """
    Create a complete pipeline from configuration dictionary.
    
    Configuration structure:
    {
        'name': 'Pipeline Name',
        'stages': [
            {
                'name': 'Stage Name',
                'batcher': {'type': 'full'},  # or {'type': 'chunk', 'chunk_size': 100}
                'evaluators': {
                    'pool_size': 5,
                    'committee_size': 3,
                    'sampling': 'random',  # or 'identity'
                    'aggregation': 'mean',  # or 'median'
                    'bias_overrides': {...}  # optional
                },
                'selector': {
                    'type': 'threshold', 'threshold': 0.01  # or
                    'type': 'top_k', 'k': 5  # or
                    'type': 'top_percent', 'percent': 1.5
                },
                'max_output': 10  # optional
            }
        ]
    }
    """
    stages = []
    
    for stage_config in config['stages']:
        # Create batcher
        batcher_config = stage_config.get('batcher', {'type': 'full'})
        batcher_type = batcher_config['type']
        
        if batcher_type == 'full':
            batcher = FullBatcher()
        elif batcher_type == 'chunk':
            batcher = ChunkBatcher(batcher_config['chunk_size'])
        elif batcher_type == 'stream':
            batcher = StreamBatcher()
        else:
            raise ValueError(f"Unknown batcher type: {batcher_type}")
        
        # Create evaluators
        eval_config = stage_config['evaluators']
        pool = []
        
        for i in range(eval_config.get('pool_size', 1)):
            if 'bias_overrides' in eval_config:
                # Use specified biases
                overrides = eval_config['bias_overrides']
                profile = BiasProfile(
                    id=f"{eval_config.get('pool_prefix', 'evaluator')}_{i}",
                    pitch_sensitivity=overrides.get('pitch_sensitivity', 0.75),
                    profile_bias=overrides.get('profile_bias', 0.0),
                    noise_std=overrides.get('noise_std', 0.5)
                )
            else:
                # Generate random evaluator
                profile = BiasProfile.generate_random(
                    f"{eval_config.get('pool_prefix', 'evaluator')}_{i}"
                )
            pool.append(profile)
        
        evaluators = Evaluators(
            pool=pool,
            committee_size=eval_config.get('committee_size', len(pool)),
            sampling=eval_config.get('sampling', 'identity'),
            aggregation=eval_config.get('aggregation', 'mean')
        )
        
        # Create selector
        sel_config = stage_config['selector']
        sel_type = sel_config['type']
        
        if sel_type in ['threshold', 'fixed_threshold']:
            selector = Selector('threshold', sel_config['threshold'])
        elif sel_type == 'top_k':
            selector = Selector('top_k', sel_config['k'])
        elif sel_type == 'top_percent':
            selector = Selector('top_percent', sel_config['percent'])
        else:
            raise ValueError(f"Unknown selector type: {sel_type}")
        
        # Create stage
        stage = Stage(
            name=stage_config['name'],
            batcher=batcher,
            evaluators=evaluators,
            selector=selector,
            min_output=stage_config.get('min_output'),
            max_output=stage_config.get('max_output')
        )
        stages.append(stage)
    
    return Pipeline(name=config['name'], stages=stages)


# ==================== Utilities ====================

def get_pipeline(investor_type: str, **overrides) -> Pipeline:
    """
    Get a pipeline configuration by investor type with optional overrides.
    
    Examples:
        pipeline = get_pipeline('angel_investor')
        pipeline = get_pipeline('general_vc', max_output=10)
    """
    if investor_type not in INVESTOR_CONFIGS:
        raise ValueError(f"Unknown investor type: {investor_type}")
    
    # Deep copy configuration to avoid mutations
    config = json.loads(json.dumps(INVESTOR_CONFIGS[investor_type]))
    
    # Apply overrides
    for key, value in overrides.items():
        if key == 'stages' and isinstance(value, list):
            config['stages'] = value
        elif '.' in key:  # Handle nested keys like 'stages.0.max_output'
            parts = key.split('.')
            target = config
            for part in parts[:-1]:
                if part.isdigit():
                    target = target[int(part)]
                else:
                    target = target[part]
            target[parts[-1]] = value
        else:
            config[key] = value
    
    return create_pipeline_from_config(config)


def apply_pitch_filter(candidates: CandidateBatch, threshold: float = 0.0) -> None:
    """
    Simulate automated pitch quality improvement (e.g., via AI coaching).
    
    This models the effect of providing feedback that helps founders improve
    their pitch to at least a minimum threshold. In practice, this could be
    an LLM reviewing pitch decks and providing improvement suggestions.
    """
    candidates.pitch_qualities = np.maximum(candidates.pitch_qualities, threshold)


def run_monte_carlo(investor_type: str, 
                   n_simulations: int = 1000,
                   review_count: int = None,
                   use_pitch_filter: bool = False,
                   candidates: CandidateBatch = None) -> pd.DataFrame:
    """
    Run Monte Carlo simulation for a specific investor type.
    
    Parameters:
        investor_type: One of the predefined investor types
        n_simulations: Number of simulation runs
        review_count: Number of candidates to review (None to use config default)
        use_pitch_filter: Whether to apply pitch quality filtering
        candidates: Pre-generated candidate pool (None to generate)
    
    Returns:
        DataFrame with simulation results
    """
    
    if candidates is None:
        candidates = CandidateBatch.generate(30000, seed=42)
    
    # Get review count from config if not provided
    if review_count is None:
        review_count = INVESTOR_CONFIGS[investor_type].get('review_count', 1000)
    
    # Save original pitch qualities for restoration
    original_pitch = candidates.pitch_qualities.copy()
    results = []
    
    for i in tqdm(range(n_simulations), desc=f"{investor_type}"):
        # Reset pitch qualities
        candidates.pitch_qualities = original_pitch.copy()
        
        if use_pitch_filter:
            apply_pitch_filter(candidates)
        
        # Sample candidates for this simulation
        if review_count >= len(candidates):
            sample_indices = np.arange(len(candidates))
        else:
            sample_indices = np.random.choice(len(candidates), review_count, replace=False)
        sampled = candidates.subset(sample_indices)
        
        # Run pipeline
        pipeline = get_pipeline(investor_type)
        result = pipeline.run(sampled, seed=i)
        
        # Collect metrics
        results.append({
            'iteration': i,
            'portfolio_size': result.summary_metrics.get('portfolio_size', 0),
            'avg_true_probability': result.summary_metrics.get('avg_true_probability', 0),
            'expected_successes': result.summary_metrics.get('expected_successes', 0),
            'actual_unicorns': result.summary_metrics.get('actual_unicorns', 0),
            'portfolio_success_prob': result.summary_metrics.get('portfolio_success_prob', 0),
            'acceptance_rate': result.summary_metrics.get('acceptance_rate', 0),
            'use_pitch_filter': use_pitch_filter
        })
    
    # Restore original pitch qualities
    candidates.pitch_qualities = original_pitch
    return pd.DataFrame(results)


# ==================== Main Execution ====================

def main():
    """Run complete PRISM framework analysis comparing all investor types."""
    
    print("PRISM Framework - Production Run")
    print("=" * 60)
    
    # Generate startup population
    print("\nGenerating startup population...")
    candidates = CandidateBatch.generate(n=30000, seed=42)
    print(f"Generated {len(candidates)} startups")
    print(f"Top 5000 average probability: {np.mean(sorted(candidates.true_probabilities, reverse=True)[:5000]):.3%}")
    
    n_simulations = 100
    all_results = []
    
    print(f"\nRunning {n_simulations} simulations per investor type...")
    print("-" * 60)
    
    # Iterate directly over configurations
    for investor_type, config in INVESTOR_CONFIGS.items():
        print(f"\n{config['name']}")
        
        # Run baseline (no pitch filter)
        baseline_df = run_monte_carlo(
            investor_type, 
            n_simulations=n_simulations,
            use_pitch_filter=False,
            candidates=candidates
        )
        
        # Run with pitch filter
        filtered_df = run_monte_carlo(
            investor_type,
            n_simulations=n_simulations,
            use_pitch_filter=True,
            candidates=candidates
        )
        
        # Calculate summary statistics
        baseline_mean = baseline_df['avg_true_probability'].mean()
        filtered_mean = filtered_df['avg_true_probability'].mean()
        improvement = (filtered_mean / baseline_mean - 1) * 100 if baseline_mean > 0 else 0
        
        baseline_unicorns = baseline_df['actual_unicorns'].mean()
        filtered_unicorns = filtered_df['actual_unicorns'].mean()
        
        # Calculate quality standard deviation - key metric for selection consistency
        baseline_quality_std = baseline_df['avg_true_probability'].std()
        filtered_quality_std = filtered_df['avg_true_probability'].std()
        
        # Also track unicorn and success prob std for completeness
        baseline_unicorns_std = baseline_df['actual_unicorns'].std()
        filtered_unicorns_std = filtered_df['actual_unicorns'].std()
        baseline_success_prob_std = baseline_df['portfolio_success_prob'].std()
        filtered_success_prob_std = filtered_df['portfolio_success_prob'].std()
        
        print(f"  Portfolio size: {baseline_df['portfolio_size'].mean():.1f}")
        print(f"  Quality (no filter): {baseline_mean*100:.3f}% ± {baseline_quality_std*100:.3f}%")
        print(f"  Quality (filtered): {filtered_mean*100:.3f}% ± {filtered_quality_std*100:.3f}%")
        print(f"  Quality improvement: {improvement:+.1f}%")
        print(f"  Quality consistency: {(filtered_quality_std/baseline_quality_std - 1)*100:+.1f}%")
        print(f"  Actual unicorns: {baseline_unicorns:.2f} → {filtered_unicorns:.2f}")
        
        # Store results
        summary = {
            'investor_type': investor_type,
            'name': config['name'],
            'review_count': config.get('review_count', 1000),
            'avg_portfolio_size': baseline_df['portfolio_size'].mean(),
            'quality_no_filter': baseline_mean,
            'quality_filtered': filtered_mean,
            'quality_std_no_filter': baseline_quality_std,
            'quality_std_filtered': filtered_quality_std,
            'quality_improvement': improvement,
            'actual_unicorns_no_filter': baseline_unicorns,
            'actual_unicorns_filtered': filtered_unicorns,
            'unicorns_std_no_filter': baseline_df['actual_unicorns'].std(),
            'unicorns_std_filtered': filtered_df['actual_unicorns'].std(),
            'success_prob_no_filter': baseline_df['portfolio_success_prob'].mean(),
            'success_prob_filtered': filtered_df['portfolio_success_prob'].mean(),
            'success_prob_std_no_filter': baseline_df['portfolio_success_prob'].std(),
            'success_prob_std_filtered': filtered_df['portfolio_success_prob'].std()
        }
        
        # Store results
        summary = {
            'investor_type': investor_type,
            'name': config['name'],
            'review_count': config.get('review_count', 1000),
            'avg_portfolio_size': baseline_df['portfolio_size'].mean(),
            'quality_no_filter': baseline_mean,
            'quality_filtered': filtered_mean,
            'quality_improvement': improvement,
            'actual_unicorns_no_filter': baseline_unicorns,
            'actual_unicorns_filtered': filtered_unicorns,
            'unicorns_std_no_filter': baseline_unicorns_std,
            'unicorns_std_filtered': filtered_unicorns_std,
            'success_prob_no_filter': baseline_df['portfolio_success_prob'].mean(),
            'success_prob_filtered': filtered_df['portfolio_success_prob'].mean(),
            'success_prob_std_no_filter': baseline_success_prob_std,
            'success_prob_std_filtered': filtered_success_prob_std,
            'quality_std_no_filter': baseline_df['avg_true_probability'].std(),
            'quality_std_filtered': filtered_df['avg_true_probability'].std()
        }
        all_results.append(summary)
    
    # Create summary DataFrame and sort by quality
    summary_df = pd.DataFrame(all_results)
    summary_df = summary_df.sort_values('quality_filtered', ascending=False)
    
    # Display final rankings
    print("\n" + "=" * 60)
    print("SELECTION QUALITY RANKING (With Pitch Filter)")
    print("-" * 60)
    print(f"{'Rank':<5} {'Investor Type':<25} {'Avg Quality ± Std':<20} {'Portfolio':<10} {'Unicorns':<10}")
    print("-" * 60)
    
    for i, row in enumerate(summary_df.iterrows()):
        data = row[1]
        print(f"{i+1:<5} {data['name']:<25} "
              f"{data['quality_filtered']*100:>6.3f}% ± {data['quality_std_filtered']*100:>5.3f}%  "
              f"{data['avg_portfolio_size']:>6.1f}      "
              f"{data['actual_unicorns_filtered']:>6.2f}")
    
    # Save results
    summary_df.to_csv('prism_results_summary.csv', index=False)
    print("\nResults saved to prism_results_summary.csv")
    
    # Selection Quality Consistency Analysis
    print("\n" + "=" * 60)
    print("SELECTION QUALITY CONSISTENCY ANALYSIS")
    print("-" * 60)
    
    # Calculate coefficient of variation (std/mean) for quality
    summary_df['quality_cv'] = summary_df['quality_std_filtered'] / summary_df['quality_filtered']
    
    # Sort by CV (lower = more consistent)
    consistency_sorted = summary_df.sort_values('quality_cv')
    
    print(f"{'Investor Type':<25} {'Avg Quality':<15} {'Std Dev':<12} {'CV':<8} {'Consistency':<15}")
    print("-" * 60)
    
    for _, row in consistency_sorted.iterrows():
        cv = row['quality_cv']
        consistency = 'High' if cv < 0.1 else 'Medium' if cv < 0.2 else 'Low'
        
        print(f"{row['name']:<25} "
              f"{row['quality_filtered']*100:>6.3f}%        "
              f"{row['quality_std_filtered']*100:>6.3f}%     "
              f"{cv:>6.3f}   {consistency:<15}")
    
    # Pitch filter impact on consistency
    print("\n" + "-" * 60)
    print("PITCH FILTER IMPACT ON SELECTION CONSISTENCY")
    print("-" * 60)
    print(f"{'Investor Type':<25} {'Std Change':<15} {'CV Change':<15}")
    print("-" * 60)
    
    for _, row in summary_df.iterrows():
        std_change = (row['quality_std_filtered'] / row['quality_std_no_filter'] - 1) * 100
        cv_no_filter = row['quality_std_no_filter'] / row['quality_no_filter']
        cv_change = (row['quality_cv'] / cv_no_filter - 1) * 100
        
        print(f"{row['name']:<25} {std_change:>+6.1f}%         {cv_change:>+6.1f}%")
    
    print("\nNote: Lower CV indicates more consistent selection quality")
    print("CV = Standard Deviation / Mean (coefficient of variation)")
    print("Negative changes indicate improved consistency")


if __name__ == "__main__":
    main()