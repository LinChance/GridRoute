from setuptools import setup, find_packages
import os

# Check if README.md file exists
if os.path.exists('README.md'):
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = 'Path Planning with Straight-Line Constraints (PPSLC) benchmark'

setup(
    name='ppslc',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'openai',
        'openpyxl',
        'scipy'
    ],
    description='Path Planning with Straight-Line Constraints (PPSLC) benchmark for evaluating LLM-based path planning',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='PPSLC Team',
    url='https://github.com/your-username/ppslc',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Robotics',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'generate-data=src.data_generation:main',
            'reference-paths=src.reference_paths:main',
            'run-experiment=src.api_experiment:main',
            'evaluate=src.Indicator_evaluation:main',
            'draw-paths=src.api_path_drawing:main',
            'radar-charts=src.Radar_chart_of_resluts:main',
        ],
    },
    package_data={
        'ppslc': ['prompt.py'],
    },
)