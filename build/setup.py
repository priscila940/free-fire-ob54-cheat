from setuptools import setup, find_packages

setup(
    name="free-fire-ob54-cheat",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'free-fire-ob54-cheat=src.free_fire_ob54_cheat:main',
        ],
    },
)
