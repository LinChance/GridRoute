"""
This package contains the core modules for the PPSLC project.

Modules:
    - data_generation: Functions for generating maps and obstacles.
    - api_experiment: Code to perform LLM-based path planning experiments.
    - api_path_drawing: Utilities for plotting the generated paths.
    - Indicator_evaluation: Functions for evaluating the planned paths.
    - reference_paths: Reference implementations (e.g., Dijkstra's algorithm) for path planning.
"""

from . import data_generation
from . import api_experiment
from . import api_path_drawing
from . import Indicator_evaluation
from . import reference_paths
from . import prompt
from . import Radar_chart_of_resluts
