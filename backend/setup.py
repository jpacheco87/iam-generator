from setuptools import setup, find_packages

setup(
    name="aws-iam-generator",
    version="2.1.0",
    description="AWS CLI IAM permissions analyzer and role generator",
    author="IAM Generator Team",
    author_email="team@iamgenerator.dev",
    license="Proprietary",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.34.0",
        "click>=8.1.0",
        "pydantic>=2.5.0",
        "requests>=2.31.0",
        "PyYAML>=6.0.0",
        "python-dotenv>=1.0.0",
        "rich>=13.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.7.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "iam-generator=iam_generator.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
