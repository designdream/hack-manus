from setuptools import setup, find_packages

setup(
    name="manus-bridge",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "requests>=2.26.0",
        "pydantic>=1.8.2",
    ],
    entry_points={
        "console_scripts": [
            "manus-bridge=manus_bridge.api:start_server",
        ],
    },
    author="Manus Bridge Team",
    author_email="info@example.com",
    description="A bridge between manus-manager and Manus for orchestrating AI agents",
    keywords="manus, ai, agents, manager",
    python_requires=">=3.7",
)
