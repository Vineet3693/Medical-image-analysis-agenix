from setuptools import setup, find_packages

setup(
    name="mia",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "langgraph",
        "pydantic",
        "google-generativeai",
        "openai",
        "reportlab",
        "Pillow",
        "python-dotenv",
        "opencv-python",
        "numpy"
    ],
    author="MIA Team",
    description="Medical Image Analysis System",
)
